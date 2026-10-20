"""
Aplicación Principal Streamlit
Sistema de Relevamiento Comunitario e Interacción Ciudadana
Centro de Atención Primaria de la Salud (CAPS) "Dr. Luis Gianotti" - Oro Verde, Entre Ríos
Cátedra: Introducción a los Sistemas de Salud - Bioingeniería (Facultad de Ingeniería - UNER)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime, date

# Importación de módulos arquitectónicos locales
import database as db
import ai_triage as triage

# Configuración institucional de la página
st.set_page_config(
    page_title="Relevamiento Ciudadano | CAPS Dr. Luis Gianotti",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialización segura de la base de datos relacional SQLite
db.inicializar_base_datos()

# Estilos CSS personalizados para identidad visual sanitaria, accesibilidad y diseño móvil
st.markdown("""
<style>
    /* Tipografía y paleta cromática sanitaria */
    .main-header {
        background: linear-gradient(135deg, #0e4d64 0%, #177394 100%);
        color: #ffffff;
        padding: 1.5rem 1.8rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 14px rgba(14, 77, 100, 0.15);
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.85rem;
        font-weight: 700;
        color: #ffffff;
    }
    .main-header p {
        margin: 0.4rem 0 0 0;
        font-size: 1.05rem;
        opacity: 0.92;
    }
    .kpi-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.1rem;
        border-left: 5px solid #177394;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 0.8rem;
    }
    .badge-urgencia-critica, .badge-prioridad-critica {
        background-color: #ffebee;
        color: #c62828;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-urgencia-alta, .badge-prioridad-alta {
        background-color: #fff3e0;
        color: #ef6c00;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-prioridad-media {
        background-color: #fffde7;
        color: #f57f17;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-prioridad-baja {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-area-servicio {
        background-color: #e0f2f1;
        color: #00695c;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-estado {
        background-color: #ede7f6;
        color: #4527a0;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    /* Estilos para Talleres Comunitarios del CIC Gianotti */
    .badge-cat-materno {
        background-color: #fce4ec;
        color: #ad1457;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.76rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-cat-prevencion {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.76rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-cat-derechos {
        background-color: #e1f5fe;
        color: #0277bd;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.76rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-cat-saludmental {
        background-color: #fff3e0;
        color: #ef6c00;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.76rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-cat-nutricion {
        background-color: #e0f2f1;
        color: #00695c;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.76rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .taller-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 1.2rem;
        min-height: 270px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .taller-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(14, 77, 100, 0.08);
        border-color: #cbd5e1;
    }
    .taller-titulo {
        font-size: 1.18rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0.5rem 0 0.4rem 0;
        line-height: 1.35;
    }
    .taller-desc {
        color: #475569;
        font-size: 0.92rem;
        line-height: 1.45;
        margin-bottom: 0.8rem;
    }
    .taller-responde {
        background-color: #f8fafc;
        border-left: 3px solid #64748b;
        padding: 0.45rem 0.65rem;
        border-radius: 4px;
        font-size: 0.82rem;
        color: #334155;
        margin-bottom: 0.7rem;
    }
    .taller-lugar-horario {
        font-weight: 600;
        color: #0e4d64;
        font-size: 0.88rem;
        margin-top: auto;
        padding-top: 0.5rem;
        border-top: 1px dashed #e2e8f0;
    }
    .carrusel-hero {
        background: linear-gradient(145deg, #ffffff 0%, #f0f7f9 100%);
        border: 2px solid #177394;
        border-radius: 16px;
        padding: 1.4rem;
        box-shadow: 0 8px 24px rgba(23, 115, 148, 0.10);
        margin-bottom: 1.5rem;
    }
    .centro-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.3rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .centro-card-activo {
        background: #ffffff;
        border: 2px solid #0e4d64;
        border-radius: 12px;
        padding: 1.3rem;
        box-shadow: 0 6px 20px rgba(14, 77, 100, 0.12);
        margin-bottom: 1rem;
    }
    .centro-item-stat {
        display: flex;
        justify-content: space-between;
        padding: 0.4rem 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.88rem;
        color: #334155;
    }
    .info-box-legal {
        background-color: #f1f8e9;
        border: 1px solid #c5e1a5;
        border-radius: 8px;
        padding: 0.9rem;
        font-size: 0.88rem;
        color: #33691e;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# Barrios representativos de la localidad de Oro Verde (Entre Ríos)
BARRIOS_ORO_VERDE = [
    "Zona Centro (Oro Verde)",
    "El Triangular",
    "Loma Hermosa",
    "Polideportivo / Universitario",
    "Barrio 50 Viviendas",
    "Los Paraísos",
    "Lomas del Golf",
    "Zona Rural / Ejido",
    "Otro / No especificado"
]

# Factores de vulnerabilidad conforme a relevamiento comunitario del CIC Gianotti
FACTORES_VULNERABILIDAD_SOCIAL = [
    "Embarazo adolescente",
    "Madre adolescente",
    "Madre / padre solo",
    "Analfabetismo / baja escolaridad de padre o madre",
    "Desocupación / changas",
    "Indocumentado",
    "Ancianidad",
    "Violencia",
    "Hacinamiento"
]

FACTORES_VULNERABILIDAD_SALUD = [
    "Muerte infantil",
    "Bajo peso",
    "Esquema de vacunación incompleto o atrasado (hasta los 2 años)",
    "Discapacidad",
    "Problema de salud mental",
    "Adicciones",
    "Tabaquismo",
    "ITS (infecciones de transmisión sexual)",
    "TBC (tuberculosis)",
    "Otros"
]

# Catálogo completo de Talleres Comunitarios del CIC Dr. Luis Gianotti (Oficiales + Innovaciones Ficticias)
TALLERES_COMUNITARIOS = [
    {
        "id": "taller-01",
        "titulo": "Embarazo joven y maternidad adolescente",
        "categoria": "Materno-infantil",
        "icono": "🤰",
        "descripcion": "Controles, derechos y red de apoyo para adolescentes y jóvenes gestantes o con hijos pequeños.",
        "detalle_ampliado": (
            "Este espacio brinda acompañamiento integral durante la gestación y los primeros meses de crianza. "
            "Se abordan controles obstétricos periódicos, pautas de nutrición en el embarazo, derechos del paciente y de las personas gestantes, "
            "acceso a la Asignación Universal por Embarazo (AUE), y conformación de una red comunitaria entre pares para prevenir el aislamiento y la deserción escolar."
        ),
        "responde_a": ["Embarazo adolescente", "Madre adolescente", "Bajo peso"],
        "lugar": "CiC 'Gianotti'",
        "horario": "Miércoles · 15:00 h",
        "frecuencia": "Semanal (Duración: 1h 30m)",
        "coordinacion": "Lic. Obstétrica y Lic. en Trabajo Social",
        "requisitos": "Abierto y 100% gratuito. No se requiere obra social ni derivación médica previa. Podés concurrir acompañada.",
        "destacado_carrusel": True,
        "imagen_carrusel": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": False
    },
    {
        "id": "taller-02",
        "titulo": "Vacunas y controles de niño sano",
        "categoria": "Prevención y cuidados",
        "icono": "👶",
        "descripcion": "Revisión del carnet, aplicación de dosis pendientes y seguimiento del peso de bebés y niños.",
        "detalle_ampliado": (
            "Control integral de crecimiento y desarrollo en la primera infancia. Incluye medición de peso, talla y percentilos, "
            "revisión exhaustiva y puesta al día del Calendario Nacional de Vacunación gratuito y obligatorio, "
            "consejería en lactancia materna exclusiva y alimentación complementaria oportuna, y pesquisa temprana de retrasos del desarrollo."
        ),
        "responde_a": ["Esquema de vacunación incompleto o atrasado (hasta los 2 años)", "Bajo peso"],
        "lugar": "CiC 'Gianotti'",
        "horario": "Martes · 9:00 h",
        "frecuencia": "Semanal (Atención por orden de llegada con prioridad a lactantes)",
        "coordinacion": "Equipo de Enfermería y Médica Pediatra",
        "requisitos": "Traer DNI y libreta sanitaria o carnet de vacunas físico. Gratuito y sin turno.",
        "destacado_carrusel": True,
        "imagen_carrusel": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": False
    },
    {
        "id": "taller-03",
        "titulo": "Crianza acompañada",
        "categoria": "Materno-infantil",
        "icono": "👨‍👩‍👧",
        "descripcion": "Encuentro entre madres y padres que crían solos: rutinas, cuidados y organización del día a día.",
        "detalle_ampliado": (
            "Grupo de reflexión e intercambio para familias monoparentales o cuidadores a cargo exclusivo. "
            "Se comparten herramientas sobre límites sin violencia, establecimiento de rutinas saludables, manejo del estrés y la sobrecarga cotidiana, "
            "y articulación con servicios de apoyo escolar y cuidado infantil de Oro Verde."
        ),
        "responde_a": ["Madre / padre solo", "Madre adolescente"],
        "lugar": "CiC 'Gianotti'",
        "horario": "Viernes · 10:00 h",
        "frecuencia": "Quincenal",
        "coordinacion": "Lic. en Psicología y Operadora en Niñez y Familia",
        "requisitos": "Entrada libre y gratuita. Se cuenta con rincón infantil para quienes asistan con sus hijos.",
        "destacado_carrusel": False,
        "imagen_carrusel": "https://images.unsplash.com/photo-1536640712-4d4c36ff0e4e?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": False
    },
    {
        "id": "taller-04",
        "titulo": "Documentación y acceso a derechos",
        "categoria": "Derechos y vínculos",
        "icono": "📄",
        "descripcion": "Orientación para tramitar el DNI, alfabetización básica y acceso a programas sociales y de empleo.",
        "detalle_ampliado": (
            "Asesoramiento y gestión territorial para la regularización documentaria de personas indocumentadas o con trámites pendientes en el Registro Civil. "
            "Acompañamiento en inscripción a programas de terminalidad educativa (Plan Fines, becas Progresar), tarifa social de servicios básicos "
            "y vinculación con la oficina de empleo y capacitación laboral municipal."
        ),
        "responde_a": ["Indocumentado", "Analfabetismo / baja escolaridad de padre o madre", "Desocupación / changas"],
        "lugar": "CiC 'Gianotti'",
        "horario": "Jueves · 14:00 h",
        "frecuencia": "Semanal",
        "coordinacion": "Trabajadoras Sociales y Asesoría Legal Comunitaria",
        "requisitos": "100% gratuito. Acercate con cualquier constancia o dato previo que dispongas.",
        "destacado_carrusel": False,
        "imagen_carrusel": "https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": False
    },
    {
        "id": "taller-05",
        "titulo": "Escucha y prevención de consumos",
        "categoria": "Salud mental y consumos",
        "icono": "🤝",
        "descripcion": "Espacio grupal y confidencial sobre alcohol, drogas y tabaco, con apoyo para dejar de fumar.",
        "detalle_ampliado": (
            "Dispositivo grupal de umbral bajo, abierto, no sancionatorio y estrictamente confidencial. "
            "Aborda estrategias de reducción de daños para consumos problemáticos de alcohol y sustancias, "
            "acompañamiento para la cesación tabáquica con seguimiento médico, y apoyo terapéutico para familiares y referentes afectivos."
        ),
        "responde_a": ["Adicciones", "Tabaquismo"],
        "lugar": "CiC 'Gianotti'",
        "horario": "Lunes · 17:00 h",
        "frecuencia": "Semanal",
        "coordinacion": "Equipo Interdisciplinario de Salud Mental (Psicólogo y Médico Generalista)",
        "requisitos": "Espacio anónimo, confidencial y gratuito. Podés sumarte en cualquier momento del año.",
        "destacado_carrusel": True,
        "imagen_carrusel": "https://images.unsplash.com/photo-1573497620053-ea5300f94f21?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": False
    },
    {
        "id": "taller-06",
        "titulo": "Salud mental y acompañamiento en duelos",
        "categoria": "Salud mental y consumos",
        "icono": "🌱",
        "descripcion": "Taller de contención emocional para personas con padecimiento mental o que atraviesan pérdidas.",
        "detalle_ampliado": (
            "Taller de sostén emocional para personas que transitan procesos de duelo por fallecimiento de familiares, "
            "pérdidas perinatales o infantiles, rupturas vinculares traumáticas o situaciones de sufrimiento psíquico. "
            "Facilita la elaboración comunitaria del dolor, promoviendo redes de cuidado mutuo y recursos personales de afrontamiento."
        ),
        "responde_a": ["Problema de salud mental", "Muerte infantil", "Violencia"],
        "lugar": "CiC 'Gianotti'",
        "horario": "Martes · 16:00 h",
        "frecuencia": "Semanal",
        "coordinacion": "Lic. en Psicología y Acompañante Terapéutica",
        "requisitos": "Espacio cálido, respetuoso y gratuito.",
        "destacado_carrusel": False,
        "imagen_carrusel": "https://images.unsplash.com/photo-1516307365426-bea591f05011?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": False
    },
    {
        "id": "taller-07",
        "titulo": "Vínculos sin violencia",
        "categoria": "Derechos y vínculos",
        "icono": "🛡️",
        "descripcion": "Información sobre tipos de violencia, canales de ayuda y cómo armar un plan de cuidado.",
        "detalle_ampliado": (
            "Espacio de sensibilización, detección temprana y acompañamiento ante situaciones de violencia por razones de género, "
            "violencia intrafamiliar o económica. Se brinda información clara sobre la Ley 26.485, medidas cautelares de protección, "
            "elaboración de planes de seguridad domiciliarios y articulación inmediata con la Línea 144 y el juzgado de paz."
        ),
        "responde_a": ["Violencia", "Madre / padre solo"],
        "lugar": "CiC 'Gianotti'",
        "horario": "Jueves · 17:30 h",
        "frecuencia": "Semanal",
        "coordinacion": "Área de Género y Diversidad y Trabajadoras Sociales",
        "requisitos": "Asesoramiento 100% confidencial y seguro.",
        "destacado_carrusel": False,
        "imagen_carrusel": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": False
    },
    {
        "id": "taller-08",
        "titulo": "Salud sexual y prevención de ITS",
        "categoria": "Prevención y cuidados",
        "icono": "❤️",
        "descripcion": "Charla participativa sobre cuidados, testeo gratuito y métodos anticonceptivos.",
        "detalle_ampliado": (
            "Taller abierto a adolescentes, jóvenes y adultos sobre salud sexual integral, no reproductiva y reproductiva. "
            "Entrega gratuita de preservativos, anticonceptivos orales, inyectables y colocación de implantes subdérmicos (chip). "
            "Realización de testeos rápidos y voluntarios de VIH, Sífilis y Hepatitis con entrega de resultado en 15 minutos de forma confidencial."
        ),
        "responde_a": ["ITS (infecciones de transmisión sexual)", "Embarazo adolescente"],
        "lugar": "CiC 'Gianotti'",
        "horario": "Viernes · 15:00 h",
        "frecuencia": "Semanal",
        "coordinacion": "Médica Generalista y Bioquímica del Centro de Salud",
        "requisitos": "Sin turno previo ni orden médica. Gratuito y confidencial.",
        "destacado_carrusel": False,
        "imagen_carrusel": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": False
    },
    {
        "id": "taller-09",
        "titulo": "Prevención de TBC y hogares saludables",
        "categoria": "Prevención y cuidados",
        "icono": "🫁",
        "descripcion": "Síntomas, tratamiento y ventilación del hogar; consejos para viviendas con poco espacio.",
        "detalle_ampliado": (
            "Detección activa de personas con tos y catarro de más de 15 días (sintomáticos respiratorios). "
            "Estrategias prácticas de ventilación natural cruzada y control de humedad en viviendas con hacinamiento. "
            "Información sobre la gratuidad del tratamiento de la tuberculosis (TBC), seguimiento del grupo familiar conviviente y desestigmatización de la enfermedad."
        ),
        "responde_a": ["TBC (tuberculosis)", "Hacinamiento", "Tabaquismo"],
        "lugar": "CiC 'Gianotti'",
        "horario": "Miércoles · 10:00 h",
        "frecuencia": "Quincenal",
        "coordinacion": "Médico Neumonólogo y Agentes Sanitarios",
        "requisitos": "Acceso libre y gratuito.",
        "destacado_carrusel": False,
        "imagen_carrusel": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": False
    },
    {
        "id": "taller-10",
        "titulo": "Cuidados en la vejez y discapacidad",
        "categoria": "Prevención y cuidados",
        "icono": "👵",
        "descripcion": "Autonomía, prevención de caídas y apoyos para personas mayores o con discapacidad y sus cuidadores.",
        "detalle_ampliado": (
            "Taller interdisciplinario orientado al envejecimiento activo y la inclusión de personas con discapacidad. "
            "Ejercicios de equilibrio, fuerza y marcha para prevenir caídas y fracturas domiciliarias; pautas para la adaptación del baño y la cocina; "
            "asesoramiento para el Certificado Único de Discapacidad (CUD) y espacios de respiro y autocuidado para cuidadores familiares."
        ),
        "responde_a": ["Ancianidad", "Discapacidad"],
        "lugar": "CiC 'Gianotti'",
        "horario": "Lunes · 10:00 h",
        "frecuencia": "Semanal",
        "coordinacion": "Kinesióloga, Terapista Ocupacional y Cátedra de Bioingeniería (UNER)",
        "requisitos": "Abierto a adultos mayores, familiares y cuidadores. Sin costo.",
        "destacado_carrusel": True,
        "imagen_carrusel": "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": False
    },
    # TALLERES FICTICIOS INNOVADORES
    {
        "id": "taller-11",
        "titulo": "🌱 Huerta Comunitaria, Nutrición y Cocina Saludable",
        "categoria": "Salud Comunitaria y Nutrición",
        "icono": "🥦",
        "descripcion": "Cultivo agroecológico en el predio del CIC, recetas económicas de estación y control de diabetes e hipertensión.",
        "detalle_ampliado": (
            "✨ [Iniciativa Ficticia Comunitaria] Espacio práctico y colaborativo donde vecinas y vecinos aprenden a armar huertas domiciliarias orgánicas "
            "con entrega gratuita de kits de semillas del Programa ProHuerta (INTA). "
            "Incluye talleres de cocina saludable con recetas de bajo costo para el manejo de la diabetes, hipertensión arterial y desnutrición/obesidad infantil, "
            "promoviendo la soberanía alimentaria y la actividad física al aire libre."
        ),
        "responde_a": ["Bajo peso", "Desocupación / changas", "Hacinamiento"],
        "lugar": "CiC 'Gianotti' - Predio Verde",
        "horario": "Sábados · 10:00 h",
        "frecuencia": "Semanal",
        "coordinacion": "Lic. en Nutrición, Promotores Agroecológicos y Voluntariado Universitario UNER",
        "requisitos": "100% gratuito. Traer ropa cómoda. Te llevás plantines y semillas de temporada a tu casa.",
        "destacado_carrusel": True,
        "imagen_carrusel": "https://images.unsplash.com/photo-1592417817098-8f3d6eb22509?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": True
    },
    {
        "id": "taller-12",
        "titulo": "🚨 Primeros Auxilios, RCP Básico y Accidentes en el Hogar",
        "categoria": "Prevención y cuidados",
        "icono": "❤️‍🩹",
        "descripcion": "Prácticas con simuladores: Maniobra de Heimlich, quemaduras, golpes y reanimación cardiopulmonar.",
        "detalle_ampliado": (
            "✨ [Iniciativa Ficticia Comunitaria] Taller práctico de respuesta ante emergencias caseras para familias, docentes y cuidadores. "
            "Se enseña cómo desobstruir la vía aérea en lactantes y niños (asfixia por comida o juguetes), atención inicial de quemaduras, "
            "manejo de convulsiones febriles, curaciones de heridas y maniobras de RCP sólo con las manos hasta la llegada de la ambulancia. "
            "Se utiliza equipamiento de simulación médica facilitado por la Facultad de Ingeniería (UNER)."
        ),
        "responde_a": ["Muerte infantil", "Otros", "Esquema de vacunación incompleto o atrasado (hasta los 2 años)"],
        "lugar": "CiC 'Gianotti' - Salón Central",
        "horario": "Sábados · 15:30 h",
        "frecuencia": "Quincenal",
        "coordinacion": "Equipo de Bioingenieros en Salud Pública y Bomberos Voluntarios",
        "requisitos": "Sin costo. Incluye certificado de asistencia y folletería de emergencia para la heladera.",
        "destacado_carrusel": True,
        "imagen_carrusel": "https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": True
    },
    {
        "id": "taller-13",
        "titulo": "🧠 Estimulación Temprana y Rincón del Neurodesarrollo",
        "categoria": "Materno-infantil",
        "icono": "🧩",
        "descripcion": "Juegos sensoriomotores y fortalecimiento vincular para bebés y niños de 0 a 3 años.",
        "detalle_ampliado": (
            "✨ [Iniciativa Ficticia Comunitaria] Espacio de juego compartido para fortalecer el desarrollo psicomotriz, el lenguaje y la comunicación temprana. "
            "Acompañamiento especializado para familias con niños nacidos prematuros, con bajo peso o con pautas de alarma en el desarrollo motriz. "
            "Fabricación casera de juguetes sensoriales con materiales reciclados del hogar."
        ),
        "responde_a": ["Bajo peso", "Discapacidad", "Madre adolescente"],
        "lugar": "CiC 'Gianotti' - Sala de Estimulación",
        "horario": "Miércoles · 16:30 h",
        "frecuencia": "Semanal",
        "coordinacion": "Psicopedagoga, Estimuladora Temprana y Fonoaudióloga",
        "requisitos": "100% gratuito. Asistir con ropa cómoda para sentarse en colchonetas.",
        "destacado_carrusel": False,
        "imagen_carrusel": "https://images.unsplash.com/photo-1596464716127-f2a829822301?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": True
    },
    {
        "id": "taller-14",
        "titulo": "🏃 Movilidad Activa y Prevención Cardiovascular Comunitaria",
        "categoria": "Prevención y cuidados",
        "icono": "👟",
        "descripcion": "Caminatas guiadas, ejercicios de respiración, control de presión arterial y bienestar mental.",
        "detalle_ampliado": (
            "✨ [Iniciativa Ficticia Comunitaria] Grupo de actividad física adaptada para personas con sedentarismo, hipertensión arterial, sobrepeso o tabaquismo. "
            "Incluye toma de presión arterial antes y después de cada caminata, ejercicios de movilidad articular, estiramientos suaves y talleres breves "
            "sobre manejo de la ansiedad y pausas activas."
        ),
        "responde_a": ["Ancianidad", "Problema de salud mental", "Tabaquismo"],
        "lugar": "CiC 'Gianotti' - Playón Polideportivo",
        "horario": "Jueves · 9:30 h",
        "frecuencia": "Martes y Jueves",
        "coordinacion": "Prof. de Educación Física y Médico de Cabecera",
        "requisitos": "Abierto a todas las edades y niveles de condición física. Gratuito.",
        "destacado_carrusel": False,
        "imagen_carrusel": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=800&q=80",
        "es_ficticio": True
    }
]


@st.dialog("📋 Detalle del Taller Comunitario")
def mostrar_modal_taller(taller):
    st.markdown(f"### {taller['icono']} {taller['titulo']}")
    if taller.get("es_ficticio"):
        st.caption("✨ *Propuesta comunitaria complementaria desarrollada para el Centro de Salud.*")
    
    col_m1, col_m2 = st.columns([1.1, 1.0])
    with col_m1:
        st.markdown(f"**Categoría:** `{taller['categoria']}`")
        st.markdown(f"**📍 Sede:** {taller['lugar']}")
    with col_m2:
        st.markdown(f"**🕒 Día y Horario:** **{taller['horario']}**")
        st.markdown(f"**⏱️ Frecuencia:** {taller['frecuencia']}")
        
    st.markdown("---")
    if taller.get("imagen_carrusel"):
        st.image(taller["imagen_carrusel"], caption=f"Actividad en el CiC Gianotti · {taller['titulo']}", width="stretch")
        
    st.markdown("##### 🎯 Propósito y Descripción Integral")
    st.write(taller['detalle_ampliado'])
    
    st.markdown("##### 🤝 Situaciones Comunitarias a las que Responde")
    badges_html = " ".join([f"<span class='badge-urgencia-alta'>{f}</span>" for f in taller['responde_a']])
    st.markdown(badges_html, unsafe_allow_html=True)
    
    st.markdown("##### 👩‍⚕️ Equipo Profesional Coordinador")
    st.info(f"**A cargo de:** {taller['coordinacion']}")
    
    st.markdown("##### 📌 Requisitos de Asistencia")
    st.success(taller['requisitos'])
    
    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🙋 Me interesa participar / Asistir", key=f"btn_modal_int_{taller['id']}", width="stretch"):
            st.toast(f"¡Excelente! Te esperamos en {taller['horario']} en el CiC Gianotti. ¡Sin trámites previos!")
    with col_b2:
        st.link_button("📲 Consultar al CIC por WhatsApp", "https://wa.me/5493430000000", width="stretch")


def poblar_datos_ejemplo():
    """Genera datos sintéticos iniciales representativos de Oro Verde para demostración académica."""
    casos_iniciales = [
        {
            "relato": "Fui ayer a las 6 de la mañana para sacar turno con el pediatra para mi nene que tiene broncoespasmo y me dijeron que no había médicos hasta la semana que viene. Tuvimos que irnos hasta el Hospital San Roque en Paraná.",
            "edad": 32,
            "barrio": "El Triangular",
            "categoria": "Falta de profesionales",
            "sentimiento": "Extrema frustración",
            "urgencia": "Alta",
            "resumen": "Falta de pediatra para paciente pediátrico con dificultad respiratoria aguda; derivación forzada a Paraná."
        },
        {
            "relato": "La atención de las enfermeras de la mañana en la sala de vacunación fue excelente. Muy amables y pacientes con los chicos durante la campaña.",
            "edad": 45,
            "barrio": "Zona Centro (Oro Verde)",
            "categoria": "Atención adecuada / Reconocimiento",
            "sentimiento": "Positiva",
            "urgencia": "Baja",
            "resumen": "Agradecimiento y valoración positiva del servicio de vacunación y trato del personal de enfermería."
        },
        {
            "relato": "Mi abuela necesita Losartán para la presión y hace tres semanas que nos dicen que no llega el suministro del ministerio. Es jubilada y no puede costearlo en la farmacia.",
            "edad": 28,
            "barrio": "Barrio 50 Viviendas",
            "categoria": "Falta de insumos y medicamentos",
            "sentimiento": "Negativa",
            "urgencia": "Alta",
            "resumen": "Desabastecimiento sostenido de antihipertensivo (Losartán) para paciente de la tercera edad."
        },
        {
            "relato": "El día de lluvia se goteaba el techo de la sala de espera y casi se cae una señora embarazada. Además los baños públicos estaban sin agua.",
            "edad": 54,
            "barrio": "Loma Hermosa",
            "categoria": "Deficiencias de infraestructura",
            "sentimiento": "Extrema frustración",
            "urgencia": "Alta",
            "resumen": "Goteras en sala de espera con riesgo de caída para gestante y corte de servicio de agua en sanitarios."
        },
        {
            "relato": "Estuve tres horas esperando para que me atiendan en la guardia general con fiebre alta. Había un solo médico de guardia para todo el pueblo.",
            "edad": 22,
            "barrio": "Polideportivo / Universitario",
            "categoria": "Demora en la atención",
            "sentimiento": "Negativa",
            "urgencia": "Media",
            "resumen": "Demora de 3 horas por guardia con síndrome febril ante escasez de plantel médico."
        }
    ]
    
    for c in casos_iniciales:
        id_r = db.registrar_reclamo_ciudadano(c["relato"], c["edad"], c["barrio"], "Carga Académica Inicial")
        db.actualizar_resultado_triaje_ia(
            id_r, c["categoria"], c["sentimiento"], c["urgencia"], c["resumen"]
        )


# ==========================================
# BARRA LATERAL: NAVEGACIÓN Y DIAGNÓSTICO
# ==========================================
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/hospital.png", 
        width=75
    )
    st.title("CAPS Luis Gianotti")
    st.caption("Oro Verde, Entre Ríos | Sistema de Salud Primaria")
    st.markdown("---")

    menu_seleccion = st.radio(
        "Navegación del Sistema:",
        [
            "🌱 Talleres Comunitarios y Prevención",
            "🩺 Portal del Ciudadano",
            "📊 Tablero de Gestión Sanitaria",
            "📑 Fundamentación Bioingenieril & Legal"
        ],
        index=0
    )

    st.markdown("---")
    with st.expander("🌐 Hosting y Acceso Público"):
        st.caption("Esta web puede desplegarse en la nube (Streamlit Cloud, Render, VPS) o en red local. Al hostearla, cualquier persona con el link puede acceder desde su celular o PC.")

    st.markdown("---")
    st.subheader("Estado de Motor IA (Ollama)")
    ollama_ok, ollama_msg, modelos_disp = triage.verificar_disponibilidad_ollama()
    
    if ollama_ok:
        st.success(f"🟢 {ollama_msg}")
        if modelos_disp:
            modelo_activo = st.selectbox(
                "Modelo Local Activo:",
                modelos_disp,
                index=0 if triage.MODELO_PREDETERMINADO not in modelos_disp else modelos_disp.index(triage.MODELO_PREDETERMINADO)
            )
        else:
            modelo_activo = triage.MODELO_PREDETERMINADO
            st.warning("⚠️ Servicio activo pero no se detectaron modelos descargados.")
    else:
        st.error(f"🔴 {ollama_msg}")
        modelo_activo = triage.MODELO_PREDETERMINADO
        st.info("💡 Los reclamos se guardarán en SQLite y podrán ser clasificados al encender Ollama.")

    st.markdown("---")
    st.caption("Proyecto de Cátedra: *Introducción a los Sistemas de Salud*")
    st.caption("Carrera de Bioingeniería - FI-UNER")


# =====================================================================
# VISTA PRINCIPAL: TALLERES COMUNITARIOS Y PREVENCIÓN (INICIO)
# =====================================================================
if menu_seleccion == "🌱 Talleres Comunitarios y Prevención":
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <span style="font-size: 0.95rem; font-weight: 700; color: #177394; text-transform: uppercase; letter-spacing: 0.5px;">
            Talleres comunitarios · CiC "Gianotti"
        </span>
        <h1 style="font-size: 2.2rem; font-weight: 800; color: #0e4d64; margin: 0.2rem 0 0.5rem 0;">
            Talleres de prevención para tu familia
        </h1>
        <p style="font-size: 1.05rem; color: #475569; max-width: 900px; line-height: 1.5; margin-bottom: 0.5rem;">
            Marcá las situaciones que se presentan en tu hogar y te mostramos los talleres gratuitos del Centro de salud Luis A. Gianotti que pueden ayudarte.
        </p>
        <a href="https://www.facebook.com/oroverdemunicipio" target="_blank" style="color: #177394; font-weight: 600; text-decoration: underline; font-size: 0.95rem;">
            🔗 Ver la página del centro en Facebook
        </a>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECCIÓN 1: CARRUSEL INTERACTIVO DE TALLERES DESTACADOS
    # -------------------------------------------------------------
    talleres_destacados = [t for t in TALLERES_COMUNITARIOS if t.get("destacado_carrusel")]
    
    if "carrusel_idx" not in st.session_state:
        st.session_state.carrusel_idx = 0

    idx_actual = st.session_state.carrusel_idx % len(talleres_destacados)
    taller_carrusel = talleres_destacados[idx_actual]

    # Barra de navegación del carrusel
    col_tit_carr, col_nav_carr = st.columns([2.5, 1.2], vertical_alignment="center")
    with col_tit_carr:
        st.markdown(f"#### 🌟 Espacio Destacado ({idx_actual + 1}/{len(talleres_destacados)}): *{taller_carrusel['titulo']}*")
    with col_nav_carr:
        c_prev, c_ind, c_next = st.columns([1, 2, 1], vertical_alignment="center")
        with c_prev:
            if st.button("◀", key="btn_prev_carr", width="stretch", help="Taller anterior"):
                st.session_state.carrusel_idx = (idx_actual - 1) % len(talleres_destacados)
                st.rerun()
        with c_ind:
            st.markdown(f"<p style='text-align:center; font-weight:700; margin:0;'>{idx_actual + 1} / {len(talleres_destacados)}</p>", unsafe_allow_html=True)
        with c_next:
            if st.button("▶", key="btn_next_carr", width="stretch", help="Siguiente taller"):
                st.session_state.carrusel_idx = (idx_actual + 1) % len(talleres_destacados)
                st.rerun()

    # Tarjeta Hero del Carrusel
    with st.container():
        st.markdown("""<div class="carrusel-hero">""", unsafe_allow_html=True)
        col_img_carr, col_info_carr = st.columns([1.1, 1.6], gap="large")

        with col_img_carr:
            if taller_carrusel.get("imagen_carrusel"):
                st.image(taller_carrusel["imagen_carrusel"], caption=f"Sede CiC Gianotti · {taller_carrusel['horario']}", width="stretch")
            if taller_carrusel.get("es_ficticio"):
                st.info("✨ **Propuesta Comunitaria Ficticia:** Desarrollada para ampliar la oferta del centro.")

        with col_info_carr:
            badge_class = {
                "Materno-infantil": "badge-cat-materno",
                "Prevención y cuidados": "badge-cat-prevencion",
                "Derechos y vínculos": "badge-cat-derechos",
                "Salud mental y consumos": "badge-cat-saludmental",
                "Salud Comunitaria y Nutrición": "badge-cat-nutricion"
            }.get(taller_carrusel["categoria"], "badge-cat-prevencion")

            st.markdown(f"""
            <span class="{badge_class}">{taller_carrusel['categoria']}</span>
            <h2 style="font-size: 1.55rem; color: #0e4d64; margin: 0.5rem 0 0.4rem 0;">{taller_carrusel['icono']} {taller_carrusel['titulo']}</h2>
            <p style="font-size: 0.98rem; color: #334155; line-height: 1.5;">{taller_carrusel['descripcion']}</p>
            """, unsafe_allow_html=True)

            st.markdown(f"**📍 Sede y Horario:** `{taller_carrusel['lugar']}` &nbsp;|&nbsp; 🕒 **{taller_carrusel['horario']}**")
            st.markdown(f"**👥 Coordinación:** {taller_carrusel['coordinacion']}")

            st.markdown(f"**🤝 Responde a:** " + ", ".join([f"`{f}`" for f in taller_carrusel['responde_a']]))

            st.write("")
            c_det_btn, c_dir_btn = st.columns([1.5, 1])
            with c_det_btn:
                if st.button("🔍 Ver Información en Detalle", key=f"btn_hero_ver_{taller_carrusel['id']}", type="primary", width="stretch"):
                    mostrar_modal_taller(taller_carrusel)
            with c_dir_btn:
                st.link_button("📲 WhatsApp de Consultas", "https://wa.me/5493430000000", width="stretch")

        st.markdown("""</div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECCIÓN 2: FILTRO INTERACTIVO POR FACTORES DE VULNERABILIDAD
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("""
    <h3 style="color: #0e4d64; font-weight: 700; margin-bottom: 0.2rem;">
        🎯 Marcá las situaciones que se presentan en tu hogar
    </h3>
    <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 1rem;">
        Podés tildar una o más opciones para ordenar y priorizar los talleres más adecuados para tu familia.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("##### 👥 Factores de vulnerabilidad (familiar y social)")
    sel_social = st.pills(
        "Seleccioná todos los que correspondan al hogar:",
        FACTORES_VULNERABILIDAD_SOCIAL,
        selection_mode="multi",
        key="pills_factores_sociales"
    )

    st.markdown("##### 🩺 Factores de vulnerabilidad (salud)")
    sel_salud = st.pills(
        "Seleccioná las condiciones presentes en el grupo familiar:",
        FACTORES_VULNERABILIDAD_SALUD,
        selection_mode="multi",
        key="pills_factores_salud"
    )

    col_btn_limpiar, col_disclaimer = st.columns([1.2, 4], vertical_alignment="center")
    with col_btn_limpiar:
        if st.button("🔄 Limpiar selección", width="stretch"):
            st.session_state.pills_factores_sociales = []
            st.session_state.pills_factores_salud = []
            st.rerun()
    with col_disclaimer:
        st.caption("🔒 *Lo que marques no se guarda ni se envía: solo sirve para ordenar esta lista de forma totalmente anónima.*")

    # Lógica de filtrado de talleres
    factores_activos = set((sel_social or []) + (sel_salud or []))
    
    if factores_activos:
        talleres_filtrados = [
            t for t in TALLERES_COMUNITARIOS 
            if any(f in factores_activos for f in t["responde_a"])
        ]
        if not talleres_filtrados:
            st.info("ℹ️ No se encontraron talleres específicos para esa combinación puntual. Te mostramos todos los talleres del centro:")
            talleres_filtrados = TALLERES_COMUNITARIOS
        else:
            st.success(f"🎯 **Mostrando {len(talleres_filtrados)} taller(es) del centro que responden a las situaciones seleccionadas en tu hogar:**")
    else:
        talleres_filtrados = TALLERES_COMUNITARIOS
        st.markdown(f"#### Mostrando los {len(talleres_filtrados)} talleres del centro")

    # -------------------------------------------------------------
    # SECCIÓN 3: GRILLA RESPONSIVA DE TALLERES
    # -------------------------------------------------------------
    num_columnas = 3
    cols = st.columns(num_columnas)

    for i, t in enumerate(talleres_filtrados):
        col_dest = cols[i % num_columnas]
        badge_class = {
            "Materno-infantil": "badge-cat-materno",
            "Prevención y cuidados": "badge-cat-prevencion",
            "Derechos y vínculos": "badge-cat-derechos",
            "Salud mental y consumos": "badge-cat-saludmental",
            "Salud Comunitaria y Nutrición": "badge-cat-nutricion"
        }.get(t["categoria"], "badge-cat-prevencion")

        with col_dest:
            responde_texto = ", ".join(t["responde_a"])
            badge_ficticio = "<span style='float:right; font-size:0.75rem; color:#0e4d64; font-weight:600;'>✨ Ficticio</span>" if t.get("es_ficticio") else ""
            
            st.markdown(f"""
            <div class="taller-card">
                <div>
                    <div>
                        <span class="{badge_class}">{t['categoria']}</span>
                        {badge_ficticio}
                    </div>
                    <div class="taller-titulo">{t['icono']} {t['titulo']}</div>
                    <div class="taller-desc">{t['descripcion']}</div>
                    <div class="taller-responde">
                        <b>Responde a:</b> {responde_texto}
                    </div>
                </div>
                <div class="taller-lugar-horario">
                    📍 {t['lugar']}<br>
                    🕒 {t['horario']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📋 Ver Detalle e Información", key=f"btn_ver_grid_{t['id']}", width="stretch"):
                mostrar_modal_taller(t)
            st.write("")

    # -------------------------------------------------------------
    # SECCIÓN 4: DATOS DE CADA CENTRO (Página 2 del PDF)
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("""
    <div style="margin-top: 1.5rem; margin-bottom: 1rem;">
        <h2 style="font-size: 1.8rem; font-weight: 800; color: #0e4d64; margin-bottom: 0.3rem;">
            Datos de cada centro
        </h2>
        <p style="font-size: 0.95rem; color: #64748b;">
            Los talleres de esta plataforma se dictan solo en el CiC "Gianotti". Cifras anuales agregadas y anonimizadas, sin datos personales.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        st.markdown("""
        <div class="centro-card">
            <h3 style="margin-top: 0; color: #1e293b; font-size: 1.25rem;">CAPS "Santa Lucía"</h3>
            <div class="centro-item-stat"><span>Población asignada</span><b>8.400</b></div>
            <div class="centro-item-stat"><span>Consultas por año</span><b>31.500</b></div>
            <div class="centro-item-stat"><span>Profesionales del equipo</span><b>14</b></div>
            <div style="margin-top: 1rem; font-weight: 700; font-size: 0.85rem; color: #475569;">
                Actividad vinculada a los talleres (último año)
            </div>
            <div class="centro-item-stat"><span>Personas vacunadas en jornadas</span><b>110</b></div>
            <div class="centro-item-stat"><span>Jóvenes gestantes y madres en seguimiento</span><b>9</b></div>
            <div class="centro-item-stat"><span>Personas en acompañamiento consumos</span><b>6</b></div>
            <div style="margin-top: 1.2rem; text-align: center; color: #94a3b8; font-size: 0.85rem; font-weight: 600;">
                Sin talleres en esta plataforma
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        st.markdown("""
        <div class="centro-card">
            <h3 style="margin-top: 0; color: #1e293b; font-size: 1.25rem;">CAPS "Jorge Newbery"</h3>
            <div class="centro-item-stat"><span>Población asignada</span><b>6.900</b></div>
            <div class="centro-item-stat"><span>Consultas por año</span><b>24.800</b></div>
            <div class="centro-item-stat"><span>Profesionales del equipo</span><b>11</b></div>
            <div style="margin-top: 1rem; font-weight: 700; font-size: 0.85rem; color: #475569;">
                Actividad vinculada a los talleres (último año)
            </div>
            <div class="centro-item-stat"><span>Personas vacunadas en jornadas</span><b>45</b></div>
            <div class="centro-item-stat"><span>Jóvenes gestantes y madres en seguimiento</span><b>11</b></div>
            <div class="centro-item-stat"><span>Personas en acompañamiento consumos</span><b>9</b></div>
            <div style="margin-top: 1.2rem; text-align: center; color: #94a3b8; font-size: 0.85rem; font-weight: 600;">
                Sin talleres en esta plataforma
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c3:
        st.markdown("""
        <div class="centro-card-activo">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem;">
                <h3 style="margin: 0; color: #0e4d64; font-size: 1.3rem;">CiC "Gianotti"</h3>
                <span class="badge-cat-prevencion">Sede Central</span>
            </div>
            <div class="centro-item-stat"><span>Población asignada</span><b>11.200</b></div>
            <div class="centro-item-stat"><span>Consultas por año</span><b>42.300</b></div>
            <div class="centro-item-stat"><span>Profesionales del equipo</span><b>19</b></div>
            <div style="margin-top: 1rem; font-weight: 700; font-size: 0.85rem; color: #0e4d64;">
                Actividad vinculada a los talleres (último año)
            </div>
            <div class="centro-item-stat"><span>Personas vacunadas en jornadas</span><b style="color:#0e4d64;">820</b></div>
            <div class="centro-item-stat"><span>Jóvenes gestantes y madres en seguimiento</span><b style="color:#0e4d64;">38</b></div>
            <div class="centro-item-stat"><span>Personas en acompañamiento consumos</span><b style="color:#0e4d64;">56</b></div>
            <div style="margin-top: 1.2rem; text-align: center; color: #0e4d64; font-size: 0.85rem; font-weight: 700; background: #e0f2f1; padding: 6px; border-radius: 6px;">
                ✅ Centro con talleres activos en esta plataforma
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.caption("ℹ️ *Maqueta de ejemplo con datos agregados de salud comunitaria: los horarios, descripciones y cifras son ilustrativos para la cátedra de Bioingeniería.*")


# ==========================================
# VISTA 2: PORTAL DEL CIUDADANO
# ==========================================
elif menu_seleccion == "🩺 Portal del Ciudadano":
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Portal Comunitario de Salud - CAPS Dr. Luis Gianotti</h1>
        <p>Tu voz transforma la atención pública en Oro Verde. Contanos tu experiencia de forma anónima, directa y protegida.</p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_guia = st.columns([1.6, 1.0], gap="large")

    with col_form:
        st.subheader("📝 Envío de Relato o Problemática")
        st.write("Podés describir lo que te sucedió con tus propias palabras, sin casillas rígidas ni trámites burocráticos.")

        with st.form("formulario_ciudadano", clear_on_submit=True):
            relato_input = st.text_area(
                "¿Qué ocurrió en el Centro de Salud? (*)",
                placeholder="Ejemplo: Fui a las 8 am a pedir turno para odontología y me informaron que no había turnos hasta dentro de un mes...",
                height=170,
                help="Describí con la mayor cantidad de detalles posible lo sucedido, fechas o áreas involucradas."
            )

            st.markdown("##### 👤 Datos de Contexto Comunitario (Opcionales)")
            col_edad, col_barrio = st.columns(2)
            
            with col_edad:
                edad_input = st.number_input(
                    "Edad del paciente o acompañante:",
                    min_value=0,
                    max_value=120,
                    value=0,
                    step=1,
                    help="Dejá en 0 si preferís no informarla."
                )

            with col_barrio:
                barrio_input = st.selectbox(
                    "Barrio de residencia en Oro Verde:",
                    BARRIOS_ORO_VERDE,
                    index=0
                )

            st.markdown("##### 📎 Fotografía o Evidencia Gráfica Adjunta (Opcional)")
            foto_ciudadano = st.file_uploader(
                "Adjuntá una imagen si querés ilustrar tu reclamo (receta, foto de infraestructura, indicación médica):",
                type=["png", "jpg", "jpeg", "webp"],
                help="Formatos admitidos: PNG, JPG, JPEG, WEBP. Tamaño sugerido hasta 10MB."
            )

            st.markdown("""
            <div class="info-box-legal">
                🛡️ <b>Compromiso de Privacidad y Soberanía de Datos:</b> En estricto cumplimiento con la <b>Ley Nacional 25.326 de Protección de los Datos Personales de la República Argentina</b>, tu relato es procesado en servidores de cómputo 100% locales en Oro Verde mediante Inteligencia Artificial on-premise. Ningún dato sensible es transferido a la nube ni a empresas extranjeras.
            </div>
            """, unsafe_allow_html=True)

            enviado = st.form_submit_button("📤 Enviar Reporte a la Gestión Sanitaria", width="stretch")

        if enviado:
            if not relato_input.strip() or len(relato_input.strip()) < 10:
                st.error("⚠️ Por favor ingresá un relato más detallado (mínimo 10 caracteres) para permitir su análisis epidemiológico.")
            else:
                with st.spinner("Registrando reporte en la base de datos local y ejecutando triaje socio-sanitario con Ollama..."):
                    # 1. Guardar archivo fotográfico si se adjuntó
                    ruta_foto_ciudadano = None
                    if foto_ciudadano:
                        ruta_foto_ciudadano = db.guardar_archivo_adjunto(foto_ciudadano, subcarpeta="ciudadanos")

                    # 2. Persistencia inmediata en SQLite
                    edad_final = int(edad_input) if edad_input > 0 else None
                    nuevo_id = db.registrar_reclamo_ciudadano(
                        relato=relato_input,
                        edad=edad_final,
                        barrio=barrio_input,
                        canal="Portal Web Ciudadano",
                        ruta_imagen=ruta_foto_ciudadano
                    )

                    # 3. Procesamiento local con IA si el servicio está disponible
                    if ollama_ok:
                        resultado_ia = triage.procesar_triaje_con_ollama(
                            relato=relato_input,
                            modelo=modelo_activo
                        )
                        if resultado_ia.get("exito"):
                            db.actualizar_resultado_triaje_ia(
                                reporte_id=nuevo_id,
                                categoria=resultado_ia["categoria"],
                                sentimiento=resultado_ia["sentimiento"],
                                urgencia=resultado_ia["urgencia"],
                                resumen=resultado_ia["resumen"]
                            )
                            st.success(f"✅ ¡Tu reporte ha sido registrado exitosamente con el Identificador Único **#RG-{nuevo_id:04d}**!")
                            st.info(f"📋 **Diagnóstico Automático Preliminar:** Categoría: *{resultado_ia['categoria']}* | Criticidad: *{resultado_ia['urgencia']}*.")
                        else:
                            st.success(f"✅ Reporte guardado con el Identificador **#RG-{nuevo_id:04d}**.")
                            st.warning(f"⚠️ El reporte fue guardado correctamente, pero el motor IA reportó: {resultado_ia.get('error')}. Se procesará en la próxima sincronización del centro.")
                    else:
                        st.success(f"✅ Reporte registrado y resguardado en la base de datos local con ID **#RG-{nuevo_id:04d}**.")
                        st.info("ℹ️ Será clasificado automáticamente cuando el equipo técnico encienda el motor de triaje.")

    with col_guia:
        st.subheader("💡 ¿Por qué es importante tu aporte?")
        st.markdown("""
        * **Visibilidad de fallas reales:** Muchas veces los problemas en la sala de espera no llegan a oídos de los directivos ni del Ministerio de Salud.
        * **Mejora en la asignación de recursos:** Demostrar con datos cuantitativos si faltan turnos en odontología, pediatría o medicación crónica permite fundamentar pedidos de presupuesto para Oro Verde.
        * **Detección de emergencias edilicias:** Permite reportar problemas de seguridad, iluminación o higiene que comprometen la salud de la comunidad.
        """)
        
        st.image(
            "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=700&q=80",
            caption="Atención Primaria de la Salud - Promoción, Prevención y Participación Comunitaria.",
            width="stretch"
        )


# ==========================================
# VISTA 2: TABLERO DE GESTIÓN INSTITUCIONAL
# ==========================================
elif menu_seleccion == "📊 Tablero de Gestión Sanitaria":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Tablero de Gestión Sanitaria y Triaje Social</h1>
        <p>Centro de Atención Primaria de la Salud "Dr. Luis Gianotti" - Diagnóstico Situacional en Tiempo Real</p>
    </div>
    """, unsafe_allow_html=True)

    # Botón para poblar con datos de prueba si la base está vacía
    todos_reportes = db.obtener_todos_los_reportes()
    if len(todos_reportes) == 0:
        st.info("ℹ️ La base de datos local aún no tiene reportes. Podés cargar casos iniciales de demostración para evaluar el tablero.")
        if st.button("🧪 Cargar Casos de Demostración de Oro Verde"):
            poblar_datos_ejemplo()
            st.rerun()

    # Métricas epidemiológicas resumidas
    metricas = db.obtener_metricas_epidemiologicas()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(
            label="Total Reportes Poblacionales",
            value=metricas["total_reportes"],
            delta=f"{metricas['procesados_ia']} clasificados por IA"
        )
    with kpi2:
        st.metric(
            label="Casos de Alta / Inmediata Criticidad",
            value=metricas["casos_alta_criticidad"],
            delta="Requieren intervención prioritaria",
            delta_color="inverse"
        )
    with kpi3:
        frustrados = metricas["distribucion_sentimientos"].get("Extrema frustración", 0) + metricas["distribucion_sentimientos"].get("Negativa", 0)
        porc_insatisfaccion = (frustrados / metricas["total_reportes"] * 100) if metricas["total_reportes"] > 0 else 0
        st.metric(
            label="Índice de Insatisfacción Comunitaria",
            value=f"{porc_insatisfaccion:.1f}%",
            delta=f"{frustrados} relatos críticos",
            delta_color="inverse"
        )
    with kpi4:
        st.metric(
            label="Reportes Pendientes de Triaje",
            value=metricas["pendientes_ia"],
            delta="Motor IA desconectado" if metricas["pendientes_ia"] > 0 else "Al día",
            delta_color="off"
        )

    st.markdown("---")

    # Filtros interactivos para análisis situacional
    st.subheader("🔍 Filtros de Exploración y Vigilancia Sanitaria")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    
    with f_col1:
        filtro_cat = st.selectbox(
            "Filtrar por Categoría:",
            ["Todas"] + triage.CATEGORIAS_VALIDAS,
            index=0
        )
    with f_col2:
        filtro_urg = st.selectbox(
            "Filtrar por Criticidad:",
            ["Todas"] + triage.URGENCIAS_VALIDAS,
            index=0
        )
    with f_col3:
        filtro_bar = st.selectbox(
            "Filtrar por Barrio:",
            ["Todos"] + BARRIOS_ORO_VERDE,
            index=0
        )
    with f_col4:
        st.write("Acciones de Base de Datos:")
        if st.button("🔄 Reprocesar Pendientes con IA", width="stretch"):
            pendientes = [r for r in db.obtener_todos_los_reportes() if r["procesado_ia"] == 0]
            if not pendientes:
                st.info("No existen reportes pendientes de triaje.")
            elif not ollama_ok:
                st.error("No se puede reprocesar: el servicio Ollama no está disponible.")
            else:
                barra = st.progress(0)
                for idx, p in enumerate(pendientes):
                    res = triage.procesar_triaje_con_ollama(p["relato_ciudadano"], modelo=modelo_activo)
                    if res.get("exito"):
                        db.actualizar_resultado_triaje_ia(
                            p["id"], res["categoria"], res["sentimiento"], res["urgencia"], res["resumen"]
                        )
                    barra.progress((idx + 1) / len(pendientes))
                st.success("¡Reprocesamiento de pendientes completado!")
                st.rerun()

    # Obtención de registros filtrados
    reportes_filtrados = db.obtener_todos_los_reportes(
        filtro_categoria=filtro_cat,
        filtro_urgencia=filtro_urg,
        filtro_barrio=filtro_bar
    )

    df_reportes = pd.DataFrame(reportes_filtrados)

    # Visualizaciones Epidemiológicas con Plotly
    if not df_reportes.empty:
        g_col1, g_col2 = st.columns(2)

        with g_col1:
            st.markdown("##### 📌 Distribución de Problemáticas por Categoría")
            conteo_cat = df_reportes["categoria_ia"].value_counts().reset_index()
            conteo_cat.columns = ["Categoría", "Cantidad"]
            fig_cat = px.bar(
                conteo_cat,
                x="Cantidad",
                y="Categoría",
                orientation="h",
                color="Cantidad",
                color_continuous_scale="Teal",
                text="Cantidad"
            )
            fig_cat.update_layout(yaxis={'categoryorder': 'total ascending'}, height=360, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_cat, width="stretch")

        with g_col2:
            st.markdown("##### ⚠️ Matriz de Criticidad / Nivel de Urgencia Sanitaria")
            conteo_urg = df_reportes["urgencia_ia"].value_counts().reset_index()
            conteo_urg.columns = ["Nivel de Urgencia", "Cantidad"]
            color_map = {
                "Crítica/Inmediata": "#d32f2f",
                "Alta": "#f57c00",
                "Media": "#fbc02d",
                "Baja": "#388e3c",
                "Pendiente": "#9e9e9e"
            }
            fig_urg = px.pie(
                conteo_urg,
                names="Nivel de Urgencia",
                values="Cantidad",
                color="Nivel de Urgencia",
                color_discrete_map=color_map,
                hole=0.42
            )
            fig_urg.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_urg, width="stretch")

        g_col3, g_col4 = st.columns(2)
        with g_col3:
            st.markdown("##### 📍 Concentración Geográfica de Quejas por Barrio en Oro Verde")
            conteo_bar = df_reportes["barrio"].value_counts().reset_index()
            conteo_bar.columns = ["Barrio", "Reportes"]
            fig_bar = px.bar(
                conteo_bar,
                x="Barrio",
                y="Reportes",
                color="Reportes",
                color_continuous_scale="Blues"
            )
            fig_bar.update_layout(xaxis_tickangle=-30, height=340, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_bar, width="stretch")

        with g_col4:
            st.markdown("##### 🎭 Perfil de Sentimiento Social de la Población")
            conteo_sent = df_reportes["sentimiento_ia"].value_counts().reset_index()
            conteo_sent.columns = ["Sentimiento", "Cantidad"]
            color_sent = {
                "Extrema frustración": "#b71c1c",
                "Negativa": "#e57373",
                "Neutral": "#90a4ae",
                "Positiva": "#81c784",
                "Pendiente": "#cfd8dc"
            }
            fig_sent = px.bar(
                conteo_sent,
                x="Sentimiento",
                y="Cantidad",
                color="Sentimiento",
                color_discrete_map=color_sent
            )
            fig_sent.update_layout(height=340, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_sent, width="stretch")

        # Tabla interactiva con detalles de los casos
        st.markdown("---")
        st.subheader(f"📋 Registros Filtrados ({len(df_reportes)} casos encontrados)")
        
        columnas_visibles = [
            "id", "fecha_hora", "barrio", "edad", "categoria_ia", 
            "urgencia_ia", "sentimiento_ia", "resumen_ia"
        ]
        st.dataframe(
            df_reportes[columnas_visibles].rename(columns={
                "id": "ID",
                "fecha_hora": "Fecha/Hora",
                "barrio": "Barrio",
                "edad": "Edad",
                "categoria_ia": "Categoría (IA)",
                "urgencia_ia": "Urgencia (IA)",
                "sentimiento_ia": "Sentimiento (IA)",
                "resumen_ia": "Síntesis Clínica/Gestión"
            }),
            width="stretch",
            hide_index=True
        )

        with st.expander("🔍 Explorar Relatos Originales Completos"):
            for _, fila in df_reportes.iterrows():
                badge_style = "badge-urgencia-critica" if fila["urgencia_ia"] in ["Crítica/Inmediata", "Alta"] else "badge-urgencia-alta"
                st.markdown(f"""
                **Caso #RG-{fila['id']:04d}** | *{fila['fecha_hora']}* | Barrio: **{fila['barrio']}** (Edad: {fila['edad'] or 'N/I'})  
                **Categoría:** {fila['categoria_ia']} | **Urgencia:** <span class="{badge_style}">{fila['urgencia_ia']}</span> | **Sentimiento:** {fila['sentimiento_ia']}  
                > *"{fila['relato_ciudadano']}"*  
                **Síntesis IA:** {fila['resumen_ia'] or 'Pendiente'}  
                """, unsafe_allow_html=True)
                
                # Visualización de evidencia adjunta por el ciudadano si existe
                if fila.get("ruta_imagen"):
                    ruta_img_abs = os.path.join(db.DIRECTORIO_RAIZ, fila["ruta_imagen"])
                    if os.path.exists(ruta_img_abs):
                        st.image(ruta_img_abs, caption=f"Evidencia fotográfica adjunta - Caso #RG-{fila['id']:04d}", width=340)
                st.markdown("---")

        # FASE 4: EXPORTACIÓN DE RESULTADOS
        st.markdown("---")
        st.subheader("📥 Exportación de Datos para Análisis Epidemiológico e Informática Médica")
        st.write("Descargá el conjunto de datos completo o filtrado para su procesamiento en herramientas estadísticas (R, Python, SPSS, PowerBI) o archivo sanitario institucional.")

        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv_data = df_reportes.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📄 Descargar Dataset en Formato CSV (Excel/R)",
                data=csv_data,
                file_name=f"relevamiento_caps_gianotti_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                width="stretch"
            )
        with col_exp2:
            json_data = json.dumps(df_reportes.to_dict(orient="records"), indent=4, ensure_ascii=False).encode('utf-8')
            st.download_button(
                label="📦 Descargar Dataset en Formato JSON (HL7/Interoperabilidad)",
                data=json_data,
                file_name=f"relevamiento_caps_gianotti_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                width="stretch"
            )

    else:
        st.warning("⚠️ No se encontraron registros para los filtros seleccionados.")



# ==========================================
# VISTA 4: FUNDAMENTACIÓN BIOINGENIERIL & LEGAL
# ==========================================
elif menu_seleccion == "📑 Fundamentación Bioingenieril & Legal":
    st.markdown("""
    <div class="main-header">
        <h1>📑 Marco Teórico, Informática en Salud y Marco Legal</h1>
        <p>Fundamentación académica para la Asignatura Introducción a los Sistemas de Salud (Bioingeniería - UNER)</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 1. El Rol de la Informática Médica y la Bioingeniería en la Atención Primaria
    Tradicionalmente, los sistemas de información en salud (HIS/EMR) se han centrado en la facturación administrativa, el inventario de farmacia o el registro de historias clínicas hospitalarias centradas en el médico.
    
    En el nivel de **Atención Primaria de la Salud (APS)**, según los principios de la Declaración de Alma-Ata y su actualización en Astaná (2018), el pilar fundamental es la **participación comunitaria activa y el diagnóstico situacional continuo**. Este software materializa la confluencia entre la bioingeniería y la salud pública al proveer:
    - **Captura de Determinantes Sociales de la Salud:** Los relatos libres de los vecinos de Oro Verde no solo exponen fallas del efector de salud, sino barreras geográficas (transporte desde El Triangular o Loma Hermosa), socioeconómicas (acceso a medicamentos) y culturales.
    - **Transformación de Datos Cualitativos no Estructurados en Datos Cuantitativos de Gestión:** La aplicación de modelos de lenguaje natural (LLMs) permite clasificar textos subjetivos y heterogéneos en variables taxonómicas epidemiológicas estandarizadas sin forzar al ciudadano a seleccionar categorías burocráticas predefinidas.
    
    ---

    ### 2. Soberanía de Datos y Cumplimiento de la Ley Nacional 25.326
    El tratamiento de datos de salud y percepciones ciudadanas está regulado de forma estricta en la República Argentina:
    - **Ley 25.326 de Protección de los Datos Personales:** Considera los datos relativos a la salud y vivencias sensibles como **datos especialmente protegidos**.
    - **Arquitectura On-Premise con Ollama:** A diferencia de soluciones basadas en APIs comerciales cerradas (que envían el texto fuera de las fronteras soberanas a servidores extranjeros en violación del principio de transferencia internacional no consentida), la utilización de un motor local de código abierto garantiza que **ningún dato personal abandona la red local del CAPS Luis Gianotti**.
    - **Anonimización por Diseño (Privacy by Design):** El sistema desacopla los datos demográficos amplios (edad aproximada, barrio) de la identidad legal del denunciante, eliminando el temor a represalias y estimulando la veracidad del relevamiento.

    ---

    ### 3. Justificación Empírica de Inversiones en Salud Pública
    Los datos recolectados y exportables en este sistema constituyen evidencia empírica directa para:
    1. **Fundamentar reestructuración de guardias:** Demostrar estadísticamente los picos horarios y barriales de demora en la atención pediátrica o clínica general.
    2. **Justificar solicitudes presupuestarias:** Respaldar peticiones formales ante la Municipalidad de Oro Verde y el Ministerio de Salud de Entre Ríos para la compra de equipamiento electromédico (ecógrafo portátil, analizador de gases, autoclave) y refuerzo del vademécum de crónicos.
    3. **Evaluación de Calidad Percibida:** Medir el impacto de intervenciones institucionales a lo largo del tiempo comparando los índices de sentimiento y criticidad antes y después de cada mejora operativa.

    ---

    ### 4. Arquitectura de Despliegue, Hosting y Acceso Público Multi-Usuario
    Una pregunta frecuente en el diseño e implementación de sistemas de información en salud es:  
    **¿Si se hostea la aplicación web, las personas pueden verla y acceder a ella?**
    
    **Respuesta Técnica y Fundamentación Bioingenieril:**
    - **🌐 Acceso Público Universal:** **Sí, absolutamente.** Al hostear la aplicación en un servidor en la nube (como Streamlit Community Cloud, Render, Railway o un VPS institucional), la plataforma obtiene una **dirección URL pública segura con certificado SSL/HTTPS** (por ejemplo: `https://caps-gianotti-oroverde.streamlit.app`). Cualquier persona del mundo —vecinos de Oro Verde, autoridades sanitarias o docentes de la Facultad— puede abrirla desde el navegador de su teléfono celular, tablet o computadora sin necesidad de instalar Python ni ningún software adicional.
    - **🔒 Privacidad y Anonimato Ciudadano:** Dado que la aplicación está diseñada con anonimización por defecto (sin solicitar DNI ni nombre completo del ciudadano), su exposición pública resguarda en todo momento el secreto estadístico y la identidad comunitaria, garantizando estricta conformidad con la Ley 25.326.
    - **💽 Persistencia Relacional y Multimedia:** Las fotos subidas y los registros se gestionan de forma desacoplada y persistente en el servidor, permitiendo que un informe técnico o reclamo cargado desde un celular sea visible de inmediato en el tablero directivo.
    - **🤖 Comportamiento del Motor IA al Hostear:**
      - **En despliegue local (On-Premise):** Funciona con Ollama en local (`localhost:11434`) con soberanía total.
      - **En hosting en la nube:** La arquitectura es tolerante a desconexión; si Ollama no está activo en el servidor remoto, el sistema almacena los reportes de manera segura e íntegra en SQLite y notifica al usuario que se procesará automáticamente al sincronizarse o mediante un servicio de inferencia.
    """)

