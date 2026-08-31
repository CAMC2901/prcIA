# 🌍 Horizon Academy - Asistente Virtual Inteligente (RAG Pipeline)

Este proyecto es un **Asistente Virtual IA completo para Horizon Academy**, diseñado con una arquitectura **RAG (Retrieval-Augmented Generation)**. Permite a la academia responder preguntas sobre precios, niveles, horarios y matrículas basándose estrictamente en sus documentos internos, evitando alucinaciones y proporcionando un flujo automático de escalamiento a soporte humano (Google Forms).

---

## 🛠️ Tecnologías Clave y su Función en el Proyecto

### 1. **LangChain** (Orquestador Principal)
- **¿Qué es?**: El framework central que conecta todos los componentes de Inteligencia Artificial.
- **Función en el proyecto**:
  - Lee los archivos de texto (`.txt`) de la carpeta `backend/data` con `TextLoader`.
  - Divide los documentos en fragmentos óptimos con `RecursiveCharacterTextSplitter`.
  - Gestiona la plantilla del prompt (`PromptTemplate`) y la cadena de ejecución (`chain = prompt | llm | parser`).
  - Conecta la base de datos vectorial (`ChromaDB`) con los modelos de lenguaje (LLM).

### 2. **HuggingFace** (Modelo de Vectorización / Embeddings)
- **¿Qué es?**: Plataforma de modelos de IA de código abierto. Usamos el modelo `all-MiniLM-L6-v2`.
- **Función en el proyecto**:
  - Convierte el texto en español a números (vectores matemáticos de alta dimensión).
  - Funciona **100% local y gratis**, eliminando la necesidad de pagar APIs externas solo para procesar y buscar en los documentos.

### 3. **ChromaDB** (Base de Datos Vectorial)
- **¿Dónde se guarda o dónde se ve?**:
  - Se guarda automáticamente en el directorio de tu proyecto dentro de la carpeta **`chroma_db/`**.
  - Ahí se almacenan los archivos `.sqlite3` e índices vectoriales donde residen los fragmentos codificados de tus documentos de texto.
- **Función en el proyecto**:
  - Almacena los vectores generados por HuggingFace.
  - Cuando el usuario hace una pregunta, ChromaDB busca por similitud matemática los 10 fragmentos de texto más relevantes y se los entrega al modelo de IA como "Contexto".

### 4. **Google Gemini 2.5 Flash** (LLM Principal)
- **¿Qué es?**: El modelo de lenguaje avanzado de Google.
- **Función en el proyecto**: Recibe el contexto encontrado por ChromaDB y redacta una respuesta coherente y amable al usuario.

### 5. **Ollama (llama3)** (LLM de Respaldo / Fallback)
- **¿Qué es?**: Un ejecutor de modelos de IA locales.
- **Función en el proyecto**: Si la API Key de Gemini no funciona, está agotada o no responde, el sistema intercepta el error automáticamente y pasa la consulta a **Ollama (`llama3`)** localmente, garantizando que el asistente **nunca deje de responder**.

---

## 📐 Estructura del Proyecto

```text
prueba-ai/
├── backend/
│   ├── data/                 # Documentos oficiales (.txt) con precios, horarios y niveles
│   ├── main.py               # Servidor FastAPI (Endpoints /api/chat, /api/metrics, /api/config)
│   ├── rag.py                # Pipeline RAG (LangChain + ChromaDB + Gemini/Ollama)
│   ├── services.py           # Servicios de caché y métricas en vivo
│   └── requirements.txt      # Dependencias de Python
├── frontend/
│   ├── index.html            # Landing page interactiva de la academia + Interfaz de chat
│   ├── style.css             # Estilos corporativos en Azul y Blanco + Animaciones
│   └── main.js               # Lógica de cliente, transiciones SPA y comunicación API
├── chroma_db/                # Base de datos vectorial persistida en disco (creada automáticamente)
├── .env                      # Variables de entorno (API Keys, URLs)
├── .env.example              # Plantilla de variables de entorno
└── README.md                 # Guía de documentación
```

---

## 🚀 Guía de Instalación y Ejecución Paso a Paso

Cualquier persona puede clonar e iniciar este proyecto siguiendo estos pasos:

### 1. Requisitos Previos
- **Python 3.9+** instalado.
- **Node.js 18+** y `npm` instalados.
- *(Opcional)* **Ollama** instalado con el modelo llama3 (`ollama pull llama3`) para funcionamiento offline/fallback.

---

### 2. Configurar el Backend (Python)

1. Abre una terminal en la raíz del proyecto y crea un entorno virtual:
   ```bash
   python -m venv venv
   ```

2. Activa el entorno virtual:
   - **Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     venv\Scripts\activate
     ```

3. Instala todas las dependencias requeridas:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Configura el archivo de variables de entorno:
   ```bash
   cp .env.example .env
   ```
   Abre `.env` y asigna tus valores:
   ```env
   GEMINI_API_KEY=tu_api_key_de_gemini
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3
   ESCALATION_FORM_URL=https://docs.google.com/forms/d/...
   ```

---

### 3. Configurar el Frontend (Vite / Vanilla JS)

En una segunda terminal, instala las dependencias del frontend:
```bash
npm install
```

---

### 4. Iniciar los Servidores

Debes tener ambos servidores ejecutándose simultáneamente:

#### **Terminal 1: Servidor Backend (FastAPI)**
```bash
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 3000 --reload
```
*El backend escuchará en `http://localhost:3000`.*

#### **Terminal 2: Servidor Frontend (Vite)**
```bash
npm run dev
```
*El frontend se abrirá en `http://localhost:5173`.*

---

## 💡 Funcionalidades Destacadas

1. **Landing Page Corporativa de Horizon Academy**: Página institucional completa en Azul y Blanco con menú de navegación, héroe descriptivo y llamado a la acción.
2. **Asistente Virtual RAG**: Responde preguntas estrictamente basadas en la documentación real de la academia sin inventar información.
3. **Animación de Escritura ("Typing Indicator")**: Animación de tres puntos rebotando mientras el bot procesa la respuesta.
4. **Sistema de Escalamiento a Google Forms**: Si la pregunta está fuera del alcance de la documentación, el bot devuelve un mensaje cordial y habilita el botón de escalamiento a soporte humano.
5. **Métricas en Vivo**: Panel que registra en tiempo real las consultas procesadas, aciertos en caché, tasa de escalamientos y costos estimados.
