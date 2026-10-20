"""
Módulo de Inteligencia Artificial para Triaje Social Local
Sistema de Relevamiento Comunitario e Interacción Ciudadana
Centro de Atención Primaria de la Salud (CAPS) "Dr. Luis Gianotti" - Oro Verde, Entre Ríos
Integración con Ollama (100% Local y Soberanía de Datos - Ley 25.326)
"""

import json
import re
import requests
from typing import Dict, Any, Optional, Tuple

# Configuración del servidor Ollama local
URL_OLLAMA_API = "http://localhost:11434/api/generate"
URL_OLLAMA_TAGS = "http://localhost:11434/api/tags"
MODELO_PREDETERMINADO = "llama3:8b"

# Taxonomía estandarizada para triaje socio-sanitario
CATEGORIAS_VALIDAS = [
    "Demora en la atención",
    "Falta de profesionales",
    "Deficiencias de infraestructura",
    "Falta de insumos y medicamentos",
    "Trato del personal",
    "Barreras administrativas y turnos",
    "Atención adecuada / Reconocimiento",
    "Otra problemática"
]

SENTIMIENTOS_VALIDOS = [
    "Positiva",
    "Neutral",
    "Negativa",
    "Extrema frustración"
]

URGENCIAS_VALIDAS = [
    "Baja",
    "Media",
    "Alta",
    "Crítica/Inmediata"
]

PROMPT_SISTEMA_TRIAJE = """Eres un Asistente Experto en Triaje Social y Salud Pública Comunitaria asignado al Centro de Atención Primaria de la Salud (CAPS) 'Dr. Luis Gianotti' en la localidad de Oro Verde, Entre Ríos, Argentina.
Tu misión es analizar con rigor técnico, empatía y criterio epidemiológico el relato de un vecino/a de la comunidad sobre su experiencia o necesidad en el centro de salud.

Debes responder EXCLUSIVAMENTE con un objeto JSON válido (sin explicaciones previas ni posteriores, sin bloques markdown de código fuera del JSON) con la siguiente estructura estricta:
{
  "categoria": "<una de las categorías válidas exactas>",
  "sentimiento": "<uno de los sentimientos válidos exactos>",
  "urgencia": "<uno de los niveles de urgencia válidos exactos>",
  "resumen": "<síntesis técnica del reclamo en máximo 25 palabras>",
  "justificacion_criterio": "<justificación breve de la urgencia asignada>"
}

Opciones obligatorias para cada campo:
- categoria: ["Demora en la atención", "Falta de profesionales", "Deficiencias de infraestructura", "Falta de insumos y medicamentos", "Trato del personal", "Barreras administrativas y turnos", "Atención adecuada / Reconocimiento", "Otra problemática"]
- sentimiento: ["Positiva", "Neutral", "Negativa", "Extrema frustración"]
- urgencia:
    * "Baja": Sugerencias menores, agradecimientos o trámites administrativos que no impactan la salud inmediata.
    * "Media": Demoras prolongadas en sala de espera, turnos postergados para especialidades o controles de rutina.
    * "Alta": Falta de medicación crónica (hipertensión, diabetes), fallas edilicias peligrosas (falta de luz/agua, techos) o dolor moderado no atendido.
    * "Crítica/Inmediata": Síntomas de alarma pediátrica o en adultos mayores sin atención, episodios de violencia, denegación flagrante de auxilio o ruptura de cadena de frío de biológicos.

Analiza el siguiente relato del ciudadano:
"""


def verificar_disponibilidad_ollama() -> Tuple[bool, str, list]:
    """
    Comprueba si el demonio de Ollama está respondiendo en el puerto 11434
    y lista los modelos de lenguaje descargados localmente.
    """
    try:
        respuesta = requests.get(URL_OLLAMA_TAGS, timeout=3.0)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            modelos = [m.get("name") for m in datos.get("models", [])]
            return True, "Servicio Ollama operativo localmente", modelos
        return False, f"Ollama respondió con código de estado {respuesta.status_code}", []
    except requests.exceptions.ConnectionError:
        return False, "No se pudo conectar a Ollama en http://localhost:11434. Asegúrate de haber iniciado el servicio con 'ollama serve'.", []
    except Exception as e:
        return False, f"Error al consultar Ollama: {str(e)}", []


def extraer_json_de_texto(texto: str) -> Optional[Dict[str, Any]]:
    """
    Limpia y extrae un bloque JSON de la respuesta del modelo,
    incluso si contiene etiquetas markdown ```json o texto adyacente.
    """
    # 1. Intento directo
    try:
        return json.loads(texto.strip())
    except Exception:
        pass

    # 2. Búsqueda con expresión regular del bloque delimitado por llaves {}
    patron = r"\{[\s\S]*\}"
    coincidencia = re.search(patron, texto)
    if coincidencia:
        try:
            return json.loads(coincidencia.group(0))
        except Exception:
            pass

    return None


def clasificacion_heuristica_emergencia(relato: str) -> Dict[str, Any]:
    """
    Mecanismo de degradación elegante (Graceful Degradation) para informática médica.
    Si el LLM local se encuentra sobrecargado o experimenta demoras de inferencia en CPU,
    aplica reglas determinísticas basadas en términos clínicos y de gestión.
    """
    texto = relato.lower()
    
    # 1. Detección de criticidad
    if any(k in texto for k in ["asfixia", "paro", "inconsciente", "convulsion", "violencia", "sangrado grave", "bebe", "broncoespasmo"]):
        urgencia = "Crítica/Inmediata"
    elif any(k in texto for k in ["urgente", "dolor fuerte", "medicamento", "presion", "hipertension", "insulina", "gotera", "caida", "abuela", "anciano"]):
        urgencia = "Alta"
    elif any(k in texto for k in ["espera", "demora", "fila", "turno", "horas", "tarde"]):
        urgencia = "Media"
    else:
        urgencia = "Baja"

    # 2. Detección de categoría
    if any(k in texto for k in ["medico", "doctor", "pediatra", "especialista", "profesional", "enfermera"]):
        categoria = "Falta de profesionales"
    elif any(k in texto for k in ["remedio", "medicamento", "losartan", "farmacia", "insumo", "gasa", "jeringa"]):
        categoria = "Falta de insumos y medicamentos"
    elif any(k in texto for k in ["techo", "bano", "luz", "agua", "edificio", "limpieza", "asiento", "gotera"]):
        categoria = "Deficiencias de infraestructura"
    elif any(k in texto for k in ["espera", "demora", "cola", "tiempo", "tardaron"]):
        categoria = "Demora en la atención"
    elif any(k in texto for k in ["maltrato", "grito", "atencion", "mala onda", "soberbio", "trato"]):
        categoria = "Trato del personal"
    elif any(k in texto for k in ["gracias", "excelente", "amable", "felicitar", "buena"]):
        categoria = "Atención adecuada / Reconocimiento"
    else:
        categoria = "Otra problemática"

    # 3. Sentimiento
    if any(k in texto for k in ["excelente", "gracias", "felicito", "muy bien", "agradezco"]):
        sentimiento = "Positiva"
    elif any(k in texto for k in ["bronca", "indignante", "abandono", "verguenza", "desastre", "harto"]):
        sentimiento = "Extrema frustración"
    elif any(k in texto for k in ["mal", "incomodo", "queja", "reclamo", "problema"]):
        sentimiento = "Negativa"
    else:
        sentimiento = "Neutral"

    return {
        "exito": True,
        "categoria": categoria,
        "sentimiento": sentimiento,
        "urgencia": urgencia,
        "resumen": f"[Clasificación Heurística de Respaldo] {relato[:120]}...",
        "justificacion_criterio": "Asignado por degradación elegante determinística ante latencia del LLM local.",
        "metodo": "Heurístico / Respaldo"
    }


def procesar_triaje_con_ollama(
    relato: str,
    modelo: str = MODELO_PREDETERMINADO,
    timeout_segundos: int = 120
) -> Dict[str, Any]:
    """
    Envía el relato del ciudadano al modelo de lenguaje en ejecución local en Ollama
    y extrae la clasificación estructurada para el relevamiento sanitario.
    Si ocurre timeout, activa el respaldo heurístico para evitar pérdida de datos.
    """
    prompt_completo = f"{PROMPT_SISTEMA_TRIAJE}\n\"\"\"\n{relato}\n\"\"\""
    
    payload = {
        "model": modelo,
        "prompt": prompt_completo,
        "stream": False,
        "options": {
            "temperature": 0.1,  # Consistencia y rigor taxonómico
            "top_p": 0.9
        }
    }

    try:
        respuesta = requests.post(
            URL_OLLAMA_API,
            json=payload,
            timeout=timeout_segundos
        )

        if respuesta.status_code != 200:
            resp_fallback = clasificacion_heuristica_emergencia(relato)
            resp_fallback["error"] = f"Fallo Ollama ({respuesta.status_code}). Se aplicó respaldo heurístico."
            return resp_fallback

        resultado_crudo = respuesta.json().get("response", "")
        datos_json = extraer_json_de_texto(resultado_crudo)

        if not datos_json:
            resp_fallback = clasificacion_heuristica_emergencia(relato)
            resp_fallback["error"] = "Respuesta no estructurada de Ollama. Se aplicó respaldo heurístico."
            return resp_fallback

        # Validación y saneamiento de los valores devueltos
        categoria = datos_json.get("categoria", "Otra problemática")
        if categoria not in CATEGORIAS_VALIDAS:
            categoria = "Otra problemática"

        sentimiento = datos_json.get("sentimiento", "Neutral")
        if sentimiento not in SENTIMIENTOS_VALIDOS:
            sentimiento = "Neutral"

        urgencia = datos_json.get("urgencia", "Media")
        if urgencia not in URGENCIAS_VALIDAS:
            urgencia = "Media"

        resumen = datos_json.get("resumen", relato[:100] + "...")
        justificacion = datos_json.get("justificacion_criterio", "")

        return {
            "exito": True,
            "categoria": categoria,
            "sentimiento": sentimiento,
            "urgencia": urgencia,
            "resumen": resumen,
            "justificacion_criterio": justificacion,
            "metodo": f"Ollama Local ({modelo})",
            "error": None
        }

    except requests.exceptions.Timeout:
        # Degradación elegante: no bloquea ni deja en blanco la clasificación
        resp_fallback = clasificacion_heuristica_emergencia(relato)
        resp_fallback["error"] = f"Tiempo de espera agotado ({timeout_segundos}s) con Ollama. Se activó triaje heurístico de emergencia."
        return resp_fallback

    except requests.exceptions.ConnectionError:
        resp_fallback = clasificacion_heuristica_emergencia(relato)
        resp_fallback["error"] = "Ollama no conectado. Se activó triaje heurístico de respaldo."
        return resp_fallback

    except Exception as e:
        resp_fallback = clasificacion_heuristica_emergencia(relato)
        resp_fallback["error"] = f"Excepción en triaje: {str(e)}. Se activó respaldo."
        return resp_fallback
