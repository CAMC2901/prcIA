import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.services import cache_service, metrics_service
from backend.mcp_tools import get_skills_instructions
from backend.static_responses import get_static_response

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "backend" / "data"

ESCALATION_FLAG = "OUT_OF_SCOPE"
ESCALATION_FORM_URL = os.getenv("ESCALATION_FORM_URL", "https://docs.google.com/forms/d/e/1FAIpQLSdAyhhqdotfhe9bwKaCC0faNaArmJLSjQOmuD9feRl0pEd95A/viewform")
ESCALATION_MESSAGE = f"Lo siento, no tengo esa información. Por favor, contáctanos a través de nuestro formulario y un asesor humano te ayudará: {ESCALATION_FORM_URL}"

FEW_SHOT_EXAMPLES = """
User: ¿Cuál es el valor del módulo?
Context: Valor módulo bimestral (2 meses): $480.000 COP.
Assistant: El valor del módulo bimestral es de $480.000 COP.

User: ¿Cuánto me cuestan 3 módulos con el paquete trimodular?
Context: Paquete Trimodular (3 módulos): 10% de descuento sobre el valor total de los módulos.
Assistant: El valor normal de 3 módulos es $1.440.000 COP, pero con el 10% de descuento por Paquete Trimodular el costo total es de $1.296.000 COP (ahorras $144.000 COP).

User: ¿A qué hora abren los sábados?
Context: Plan Sabatino Intensivo (Sábados - 5 horas continuas): Franja Única: 8:00 AM a 1:00 PM
Assistant: Los sábados contamos con una franja única de 8:00 AM a 1:00 PM.

User: ¿Cuál es el capital de Francia?
Context: [Sin información relevante]
Assistant: OUT_OF_SCOPE
"""

SYSTEM_PROMPT = f"""
Eres un asistente virtual amable y profesional de una academia de idiomas.
Tu tarea es responder a las preguntas de los usuarios BASÁNDOTE ÚNICAMENTE en la información proporcionada en el "Contexto" y en las capacidades de cálculo descritas en tus Skills.
Mantén un tono de marca amigable, servicial y corporativo.

{get_skills_instructions()}

Restricciones:
1. SIEMPRE debes basar tus respuestas SOLO en el contexto o en las reglas de cálculo descritas en tus Skills. No uses conocimientos externos (evita alucinaciones).
2. Si la pregunta del usuario no se puede responder con el contexto ni con tus skills de cálculo, DEBES responder EXACTAMENTE con la palabra: {ESCALATION_FLAG}. No digas nada más en ese caso.
3. Sé conciso, preciso con las cifras numéricas y claro.

Ejemplos de cómo debes responder:
{FEW_SHOT_EXAMPLES}

Contexto:
{{context}}

Pregunta del usuario:
{{question}}
"""

class ChatEngine:
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        self.llm = self._initialize_llm()
        self.prompt = PromptTemplate.from_template(SYSTEM_PROMPT)

    def _initialize_llm(self):
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")

        if openai_key:
            print("ChatEngine: Initializing ChatOpenAI (gpt-4o-mini)")
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(model="gpt-4o-mini", temperature=0.1, api_key=openai_key)
            except Exception as e:
                print(f"Failed to load ChatOpenAI ({e}). Trying Gemini...")

        if gemini_key:
            print("ChatEngine: Initializing ChatGoogleGenerativeAI (Gemini 2.5 Flash)")
            return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

        print("ChatEngine: Initializing ChatOllama (Fallback)")
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.1
        )

    def _get_embeddings(self):
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def load_documents(self):
        print(f"Loading documents from {DATA_DIR}...")
        all_docs = []
        for file_path in DATA_DIR.glob("*.txt"):
            loader = TextLoader(str(file_path))
            all_docs.extend(loader.load())

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        split_docs = splitter.split_documents(all_docs)
        print(f"Created {len(split_docs)} chunks.")

        chroma_dir = str(BASE_DIR / "chroma_db")

        try:
            embeddings = self._get_embeddings()
            self.vector_store = Chroma.from_documents(
                split_docs, 
                embeddings, 
                collection_name="academy_docs",
                persist_directory=chroma_dir
            )
        except Exception as e:
            print(f"Primary embedding failed ({e}). Falling back to Ollama...")
            # Re-initialize LLM and embeddings to Ollama
            self.llm = ChatOllama(
                model=os.getenv("OLLAMA_MODEL", "llama3"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0.1
            )
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.vector_store = Chroma.from_documents(
                split_docs, 
                embeddings, 
                collection_name="academy_docs",
                persist_directory=chroma_dir
            )

        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 10})
        print("ChromaDB successfully initialized.")

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def ask(self, question: str) -> str:
        # 1. Static Response Interception (0 tokens, 0 latency)
        static_reply = get_static_response(question)
        if static_reply:
            metrics_service.record_cache_hit()
            metrics_service.record_query()
            return static_reply

        # 2. Check Cache
        cached_response = cache_service.get(question)
        if cached_response:
            metrics_service.record_cache_hit()
            metrics_service.record_query()
            return cached_response

        if not self.retriever:
            return "El sistema no está inicializado."

        docs = self.retriever.invoke(question)
        context = self.format_docs(docs)

        chain = self.prompt | self.llm | StrOutputParser()
        
        metrics_service.record_query()

        try:
            response = chain.invoke({"context": context, "question": question})
            
            # Token Estimation
            input_tokens_approx = (len(context) + len(question) + len(SYSTEM_PROMPT)) // 4
            output_tokens_approx = len(response) // 4
            metrics_service.record_tokens(input_tokens_approx, output_tokens_approx)

            # Handle Escalation
            if response.strip() == ESCALATION_FLAG:
                metrics_service.record_escalation()
                return ESCALATION_MESSAGE

            # Save to Cache and Return
            cache_service.set(question, response)
            return response
            
        except Exception as e:
            print(f"LLM Error ({e}). Falling back to Ollama...")
            try:
                self.llm = ChatOllama(
                    model=os.getenv("OLLAMA_MODEL", "llama3"),
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                    temperature=0.1
                )
                chain = self.prompt | self.llm | StrOutputParser()
                response = chain.invoke({"context": context, "question": question})
                
                # Token Estimation for fallback
                input_tokens_approx = (len(context) + len(question) + len(SYSTEM_PROMPT)) // 4
                output_tokens_approx = len(response) // 4
                metrics_service.record_tokens(input_tokens_approx, output_tokens_approx)

                if response.strip() == ESCALATION_FLAG:
                    metrics_service.record_escalation()
                    return ESCALATION_MESSAGE

                cache_service.set(question, response)
                return response

            except Exception as fallback_e:
                print(f"Fallback LLM Error: {fallback_e}")
                metrics_service.record_escalation()
                return ESCALATION_MESSAGE

chat_engine = ChatEngine()
