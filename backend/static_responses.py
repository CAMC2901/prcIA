"""
Static Responses Engine for Horizon Academy.
Intercepts common queries, greetings, identity questions, doubts, gibberish/nonsense,
and frequent requests to return instant answers with ZERO token consumption and zero LLM latency.
"""

import re
import os

ESCALATION_FORM_URL = os.getenv("ESCALATION_FORM_URL", "https://docs.google.com/forms/d/e/1FAIpQLSdAyhhqdotfhe9bwKaCC0faNaArmJLSjQOmuD9feRl0pEd95A/viewform")

GIBBERISH_RESPONSE = "No he podido entender tu mensaje. 🧐 Por favor, escribe tu consulta de forma clara sobre nuestros cursos de idiomas (Inglés, Francés, Alemán, Italiano), precios, horarios o matrículas."

STATIC_RULES = [
    # 1. SPECIFIC INTENT: LANGUAGES OFFERED & METHODOLOGY
    {
        "keywords": ["idiomas", "dictan", "ensenan", "enseñan", "ingles", "frances", "aleman", "italiano", "lenguas", "metodologia", "ofrecen"],
        "response": "En **Horizon Academy** enseñamos **Inglés, Francés, Alemán e Italiano** con metodología 100% enfocada en conversación, clases en vivo con profesores expertos y contenido digital alineado al MCER."
    },
    # 2. SPECIFIC INTENT: IDENTITY & NAME QUESTIONS
    {
        "keywords": ["como te llamas", "quien eres", "cual es tu nombre", "quien es usted", "presentate", "que eres"],
        "response": "¡Hola! Soy **Horizon**, el asistente virtual inteligente de **Horizon Academy**. Estoy aquí para ayudarte con toda la información sobre nuestros programas de idiomas, precios, horarios y matrículas."
    },
    # 3. SPECIFIC INTENT: QUESTION OPENINGS & DOUBTS ("una pregunta", "tengo una duda")
    {
        "keywords": [
            "una pregunta", "tengo una duda", "una duda", "tengo una pregunta", 
            "quisiera preguntar", "quiero consultar", "una consulta", "tengo una consulta", 
            "puedo hacer una pregunta", "quiero preguntar", "hacer una pregunta", "tengo dudas"
        ],
        "response": "¡Claro que sí! Dime cuál es tu duda o pregunta y con mucho gusto te brindaré toda la información sobre nuestros cursos, horarios, precios o matrículas."
    },
    # 4. SPECIFIC INTENT: HISTORY, EXPERIENCE & YEARS
    {
        "keywords": ["hace cuanto", "cuantos anos", "cuantos años", "cuantos anos llevan", "cuantos años llevan", "trayectoria", "fundacion", "cuanto tiempo llevan", "historia de la academia", "experiencia"],
        "response": "Horizon Academy cuenta con más de 10 años de experiencia e innovación educativa en Colombia, forming miles de estudiantes y profesionales con certificaciones internacionales."
    },
    # 5. SPECIFIC INTENT: HUMAN ASSISTANCE & DIRECT CONTACT
    {
        "keywords": ["humano", "asesor", "persona", "agente", "hablar con alguien", "atencion al cliente", "soporte humano", "hablar con un asesor"],
        "response": f"¡Por supuesto! Si deseas hablar directamente con un asesor humano de Horizon Academy, por favor diligencia nuestro formulario oficial aquí: {ESCALATION_FORM_URL}"
    },
    # 6. SPECIFIC INTENT: SCHEDULE PROBLEMS & CHANGES
    {
        "keywords": ["problema con el horario", "problema de horario", "cambiar de horario", "cambio de horario", "cruce de horario", "cruce de clases", "no puedo asistir", "reposicion de clase", "falte a clase", "perdi una clase"],
        "response": "Si presentas un cruce de horario o requieres cambiarte de grupo, debes enviar una solicitud formal a la secretaría académica a través de nuestro formulario de soporte: " + ESCALATION_FORM_URL + ". Los cambios se aprueban según disponibilidad de cupo en la primera semana de cada módulo."
    },
    # 7. SPECIFIC INTENT: PAYMENTS, BILLING & REFUNDS
    {
        "keywords": ["devolucion", "reembolso", "problema con el pago", "error de pago", "factura electronica", "metodo de pago", "transferencia no refleja", "medios de pago", "PSE", "tarjeta de credito"],
        "response": "Para dudas sobre transacciones, medios de pago (PSE, tarjeta, transferencia), facturación electrónica o solicitudes de reembolso, ponte en contacto con nuestro departamento de cartera aquí: " + ESCALATION_FORM_URL
    },
    # 8. SPECIFIC INTENT: PLACEMENT TESTS & EVALUATIONS
    {
        "keywords": ["examen de clasificacion", "prueba de nivel", "saber mi nivel", "homologacion", "evaluacion inicial", "nivelamento"],
        "response": "Realizamos exámenes de clasificación online y presenciales para evaluar tu nivel actual (A1 a C1). Si tienes conocimientos previos, puedes agendar tu examen comunicándote por nuestro formulario: " + ESCALATION_FORM_URL
    },
    # 9. SPECIFIC INTENT: CERTIFICATES & DIPLOMAS
    {
        "keywords": ["certificado", "diploma", "constancia de estudio", "certificado de notas", "descargar certificado", "certificacion mcer"],
        "response": "Los certificados de nivel (alineados al Marco Común Europeo MCER) se expiden al finalizar y aprobar los módulos correspondientes. Si necesitas una constancia de estudio vigente, solicítala mediante nuestro formulario: " + ESCALATION_FORM_URL
    },
    # 10. SPECIFIC INTENT: REQUIREMENTS & REGISTRATION PROCESS
    {
        "keywords": ["requisitos para inscribirme", "como me inscribo", "proceso de matricula", "documentos para ingresar", "como matricularme"],
        "response": "Para inscribirte solo necesitas tu documento de identidad y diligenciar el formulario de matrícula. No requerimos conocimientos previos para el Nivel A1. ¡Puedes matricularte directamente o solicitar asesoría personalizada aquí: " + ESCALATION_FORM_URL + "!"
    },
    # 11. SPECIFIC INTENT: MODALITIES (ONLINE VS PRESENCIAL)
    {
        "keywords": ["modalidad", "virtual o presencial", "clases online", "clases virtuales", "remoto", "en vivo"],
        "response": "Contamos con dos modalidades totalmente equivalentes: **Virtual En Vivo** (vía plataforma interactiva con profesor en directo) y **Presencial** en nuestras sedes. Ambas modalidades incluyen el mismo material digital y certificación."
    },
    # 12. SPECIFIC INTENT: CORPORATE & GROUP PLANS
    {
        "keywords": ["empresas", "planes corporativos", "descuento para empresas", "grupos empresariales", "capacitacion empresarial"],
        "response": "Ofrecemos planes de formación lingüística para empresas con flexibilidad de horarios e informes de progreso para gestión de talento humano. Solicita una propuesta corporativa mediante nuestro formulario: " + ESCALATION_FORM_URL
    },
    # 13. SPECIFIC INTENT: LOCATION & PHYSICAL CAMPUS
    {
        "keywords": ["ubicacion", "direccion", "donde quedan", "donde estan ubicados", "sede principal", "parqueadero"],
        "response": "Nuestra sede principal de Horizon Academy cuenta con instalaciones modernas, aulas con pantallas interactivas y parqueadero para estudiantes. Para atención presencial, comunícate previamente en secretaría."
    },
    # 14. GENERAL GREETINGS & PLEASANTRIES (Fallback for standalone greetings)
    {
        "keywords": ["hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "hey", "saludos", "que tal", "inicio"],
        "response": "¡Hola! Bienvenid@ a **Horizon Academy**. 🌍 Soy tu asistente virtual inteligente. ¿En qué te puedo ayudar hoy? Puedes preguntarme sobre precios, programas de idiomas, horarios, certificados o formas de pago."
    },
    # 15. THANKS & FAREWELLS
    {
        "keywords": ["gracias", "muchas gracias", "chao", "adios", "hasta luego", "excelente gracias", "vale gracias", "ok gracias"],
        "response": "¡Con mucho gusto! 😊 Estamos para servirte en Horizon Academy. ¡Que tengas un excelente día!"
    }
]

KEYBOARD_PATTERNS = ["qwerty", "asdfgh", "zxcvbn", "123456", "hjkl", "dfghj"]

def normalize_text(text: str) -> str:
    """Removes accents, punctuation, and converts text to lower case for reliable matching."""
    text = text.lower().strip()
    replacements = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("ü", "u"), ("ñ", "n"), ("?", ""), ("¿", ""), ("!", ""), ("¡", ""),
        (",", ""), (".", ""), (";", ""), (":", "")
    )
    for a, b in replacements:
        text = text.replace(a, b)
    return text

def is_gibberish(text: str) -> bool:
    """
    Detects keyboard mashing, random consonants, or nonsense strings.
    Examples: 'hdysvbfs', 'dvcyusv', 'asdfghjkl', 'qwertyuiop'
    """
    cleaned = normalize_text(text).replace(" ", "")
    if not cleaned:
        return True
    
    # Check for keyboard sequence patterns (e.g. 'qwertyuiop', 'asdfghjkl')
    for pat in KEYBOARD_PATTERNS:
        if pat in cleaned:
            return True

    # Check for short repeated characters (e.g. 'aaaaa', 'hhhhh')
    if len(set(cleaned)) == 1 and len(cleaned) > 2:
        return True
        
    # Check vowel density and consonant streaks for strings of length >= 4
    if len(cleaned) >= 4:
        vowel_count = sum(1 for char in cleaned if char in "aeiou")
        vowel_ratio = vowel_count / len(cleaned)
        
        # Less than 15% vowels in a word of 4+ characters is almost certainly gibberish in Spanish/English
        if vowel_ratio < 0.15:
            return True
            
        # 5 or more consecutive consonants without a vowel
        consonants_streak = 0
        for char in cleaned:
            if char.isalpha() and char not in "aeiou":
                consonants_streak += 1
                if consonants_streak >= 5:
                    return True
            else:
                consonants_streak = 0

    return False

def get_static_response(user_query: str):
    """
    Checks if user_query matches any static FAQ pattern or is gibberish.
    Returns response string if matched, or None if query requires RAG / LLM.
    """
    normalized_query = normalize_text(user_query)
    
    # 1. Check each static rule in priority order
    for rule in STATIC_RULES:
        for kw in rule["keywords"]:
            normalized_kw = normalize_text(kw)
            if normalized_kw in normalized_query:
                return rule["response"]
                
    # 2. Anti-Gibberish Verification Check
    if is_gibberish(user_query):
        return GIBBERISH_RESPONSE

    return None
