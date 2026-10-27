"""
=================================================================================================
UNIVERSIDAD NACIONAL DE ENTRE RÍOS (UNER) - FACULTAD DE INGENIERÍA (FIUNER)
Cátedra: Introducción a los Sistemas de Salud | Bioingeniería
Proyecto: Plataforma de trazabilidad de indicadores de la salud y gestión de talleres comunitarios
          mediante el relevamiento de datos ponderados en la "Planilla de Relevamiento de
          Agentes Sanitarios" utilizada por la plataforma "RELEVAR" para la comunidad de Oro Verde.
Efector de Salud Colaborador: Centro Integrador Comunitario (CiC) "Dr. Luis Gianotti" - Oro Verde
=================================================================================================
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

# Configuración institucional de la aplicación
st.set_page_config(
    page_title="RELEVAR | Trazabilidad & Talleres - CiC Gianotti & FIUNER",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialización segura de la base de datos y catálogo de talleres
db.inicializar_base_datos()
db.inicializar_talleres_predeterminados()

# -----------------------------------------------------------------------------------------------
# ESTILOS CSS PROFESIONALES: IDENTIDAD VISUAL SANITARIA, ACCESIBILIDAD Y DISEÑO RESPONSIVO
# -----------------------------------------------------------------------------------------------
st.markdown("""
<style>
    /* Tipografía y paleta institucional */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0e4d64 0%, #155e75 50%, #0891b2 100%);
        color: #ffffff;
        padding: 1.8rem 2.2rem;
        border-radius: 14px;
        margin-bottom: 1.6rem;
        box-shadow: 0 8px 24px rgba(14, 77, 100, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.02rem;
        opacity: 0.95;
        line-height: 1.45;
    }
    .subtag-header {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.5rem;
    }

    /* Tarjetas y Badges */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        margin-bottom: 0.8rem;
        transition: transform 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
    }
    .kpi-num {
        font-size: 2rem;
        font-weight: 800;
        color: #0e4d64;
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.3rem;
    }

    .badge-prioridad-critica {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-prioridad-alta {
        background-color: #ffedd5;
        color: #c2410c;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-prioridad-moderada {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-prioridad-baja {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-poblacion-fiuner {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.76rem;
    }
    .badge-poblacion-oroverde {
        background-color: #f3e8ff;
        color: #6b21a8;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.76rem;
    }

    /* Tarjetas de Talleres Comunitarios */
    .taller-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 1.2rem;
        min-height: 290px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .taller-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(14, 77, 100, 0.10);
        border-color: #0891b2;
    }
    .taller-titulo {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0.5rem 0 0.4rem 0;
        line-height: 1.35;
    }
    .taller-desc {
        color: #475569;
        font-size: 0.90rem;
        line-height: 1.45;
        margin-bottom: 0.8rem;
    }
    .taller-responde {
        background-color: #f8fafc;
        border-left: 3px solid #0891b2;
        padding: 0.45rem 0.65rem;
        border-radius: 4px;
        font-size: 0.80rem;
        color: #334155;
        margin-bottom: 0.7rem;
    }
    .taller-lugar-horario {
        font-weight: 600;
        color: #0e4d64;
        font-size: 0.85rem;
        margin-top: auto;
        padding-top: 0.5rem;
        border-top: 1px dashed #e2e8f0;
    }

    /* Hero Carrusel */
    .carrusel-hero {
        background: linear-gradient(145deg, #ffffff 0%, #f0fdf4 50%, #f0fdfa 100%);
        border: 2px solid #0891b2;
        border-radius: 16px;
        padding: 1.4rem;
        box-shadow: 0 8px 28px rgba(8, 145, 178, 0.12);
        margin-bottom: 1.5rem;
    }

    /* Centro Cards */
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
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 0.9rem;
        font-size: 0.88rem;
        color: #166534;
        margin-top: 1rem;
    }
    .suggestion-box {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1px solid #fde68a;
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------------------------
# CONSTANTES METODOLÓGICAS DEL PROYECTO (PLANILLA RELEVAR & FIUNER)
# -----------------------------------------------------------------------------------------------
ZONAS_RESIDENCIA = [
    "Residente de Oro Verde",
    "Estudiante",
    "Otro/Foráneo"
]
BARRIOS_ORO_VERDE = ZONAS_RESIDENCIA
ORO_VERDE = ZONAS_RESIDENCIA

CARRERAS_FIUNER = [
    "Bioingeniería",
    "Licenciatura en Bioinformática",
    "Tecnicatura Universitaria en Medicina Nuclear",
    "Tecnicatura Universitaria en Prótesis y Órtesis",
    "Posgrado / Doctorado en Ingeniería",
    "Docente / Investigador / No Docente"
]

ANOS_CURSADO = [
    "1er Año (Ingreso y Adaptación)",
    "2do Año",
    "3er Año",
    "4to Año",
    "5to Año (Proyecto Final / Tesis)",
    "Egresado Reciente"
]

# DICCIONARIO MAESTRO DE FACTORES DE VULNERABILIDAD CON PONDERACIÓN MATEMÁTICA
# Ponderación basada en severidad e impacto sobre la salud biopsicosocial (Sumatoria total: 110)
FACTORES_VULNERABILIDAD_PONDERADOS = {
    # 🧠 Salud Mental y Carga Cognitiva / Universitaria
    "Estrés académico o laboral severo / agotamiento cognitivo": {
        "categoria": "Salud Mental", "peso": 8, "descripcion": "Sobrecarga sostenida, sensación de desborde y fatiga mental continua."
    },
    "Episodios frecuentes de ansiedad o angustia": {
        "categoria": "Salud Mental", "peso": 9, "descripcion": "Crisis de angustia, opresión en el pecho o pánico ante exámenes/rutina."
    },
    "Trastornos del sueño o insomnio crónico": {
        "categoria": "Salud Mental", "peso": 7, "descripcion": "Dificultad para conciliar el sueño, despertar precoz o menos de 5h diarias."
    },
    "Aislamiento social / desarraigo familiar": {
        "categoria": "Salud Mental", "peso": 7, "descripcion": "Lejanía de los seres queridos, soledad no deseada y falta de red local."
    },
    "Problema de salud mental diagnosticado sin apoyo": {
        "categoria": "Salud Mental", "peso": 9, "descripcion": "Cuadro depresivo o de ansiedad sin acompañamiento terapéutico activo."
    },

    # 🩺 Salud Física, Nutrición y Hábitos
    "Dolores osteomusculares o cefaleas frecuentes": {
        "categoria": "Salud Física", "peso": 5, "descripcion": "Contracturas cervicales, lumbalgia o dolor de cabeza por postura y pantallas."
    },
    "Mala nutrición o salteo recurrente de comidas": {
        "categoria": "Salud Física", "peso": 6, "descripcion": "Omisión de comidas clave, abuso de ultraprocesados por falta de tiempo/recursos."
    },
    "Sedentarismo o inactividad física severa": {
        "categoria": "Salud Física", "peso": 5, "descripcion": "Ausencia total de actividad corporal o caminatas en la rutina semanal."
    },
    "Enfermedad crónica sin control regular": {
        "categoria": "Salud Física", "peso": 7, "descripcion": "Asma, diabetes, hipertensión o celiaquía sin chequeo en el último año."
    },
    "Esquema de vacunación incompleto o desactualizado": {
        "categoria": "Salud Física", "peso": 5, "descripcion": "Dosis faltantes de antitetánica, hepatitis B, triple viral o COVID-19."
    },
    "Consumo problemático de sustancias (alcohol, tabaco o psicofármacos)": {
        "categoria": "Salud Física", "peso": 8, "descripcion": "Uso riesgoso o no prescripto para regular el estrés o la vigilia."
    },

    # 🏠 Socio-Habitacional y Cuidados (Planilla de Agentes Sanitarios)
    "Inestabilidad económica severa / dificultad de sustento": {
        "categoria": "Socio-Habitacional", "peso": 8, "descripcion": "Complicación crítica para pagar alquiler, fotocopias, transporte o comida."
    },
    "Vivienda precaria / hacinamiento en el hogar": {
        "categoria": "Socio-Habitacional", "peso": 7, "descripcion": "Condiciones inadecuadas de habitabilidad, humedad o falta de espacio de estudio."
    },
    "Embarazo o maternidad/paternidad en edad temprana": {
        "categoria": "Socio-Habitacional", "peso": 8, "descripcion": "Crianza a cargo en juventud con requerimiento de red comunitaria."
    },
    "Persona a cargo de cuidados familiares intensivos": {
        "categoria": "Socio-Habitacional", "peso": 6, "descripcion": "Cuidado regular de niños pequeños, adultos mayores o familiares con discapacidad."
    },
    "Situaciones de violencia o vulneración de derechos": {
        "categoria": "Socio-Habitacional", "peso": 10, "descripcion": "Experiencias de maltrato, violencia de género o discriminación activa."
    }
}

# DICCIONARIO DE FACTORES PROTECTORES CON PONDERACIÓN (Sumatoria total: 100)
FACTORES_PROTECTORES_PONDERADOS = {
    "Cuenta con red sólida de amigos o compañeros": {
        "peso": 15, "descripcion": "Compañeros de estudio o amistades con quienes dialogar y compartir vivencias."
    },
    "Tiene cobertura médica o sabe cómo atenderse en el CIC": {
        "peso": 12, "descripcion": "Obra social, seguro universitario o conocimiento de los servicios del CiC Gianotti."
    },
    "Realiza actividad física o deporte regular (2+ veces/semana)": {
        "peso": 12, "descripcion": "Deporte, gimnasio, caminata en el polideportivo o bicicleta en Oro Verde."
    },
    "Mantiene rutinas ordenadas de descanso y alimentación": {
        "peso": 12, "descripcion": "Horarios estables de sueño y al menos 3 comidas equilibradas al día."
    },
    "Dedica tiempo semanal a hobbies y esparcimiento": {
        "peso": 12, "descripcion": "Música, lectura no académica, arte, naturaleza o desconexión digital."
    },
    "Dispone de un entorno tranquilo para estudiar": {
        "peso": 12, "descripcion": "Lugar iluminado, silencioso y con conectividad para cursar y rendir."
    },
    "Siente que puede pedir ayuda ante un malestar": {
        "peso": 15, "descripcion": "Predisposición y confianza para consultar a un profesional o tutor ante una crisis."
    },
    "Participa en actividades o talleres comunitarios": {
        "peso": 10, "descripcion": "Interés en espacios del CIC, voluntariado, centro de estudiantes o clubes de Oro Verde."
    }
}

PESO_TOTAL_VULNERABILIDAD = sum(f["peso"] for f in FACTORES_VULNERABILIDAD_PONDERADOS.values())
PESO_TOTAL_PROTECCION = sum(f["peso"] for f in FACTORES_PROTECTORES_PONDERADOS.values())


def calcular_indices_sanitarios(factores_v_sel: list, factores_p_sel: list):
    """
    Calcula el Índice de Vulnerabilidad Ponderada (IVP), Índice de Factores Protectores (IFP)
    y el Índice de Riesgo Ponderado con su semáforo de prioridad sanitaria.
    """
    suma_v = sum(FACTORES_VULNERABILIDAD_PONDERADOS[v]["peso"] for v in factores_v_sel if v in FACTORES_VULNERABILIDAD_PONDERADOS)
    suma_p = sum(FACTORES_PROTECTORES_PONDERADOS[p]["peso"] for p in factores_p_sel if p in FACTORES_PROTECTORES_PONDERADOS)

    ivp = round((suma_v / PESO_TOTAL_VULNERABILIDAD) * 100, 1)
    ifp = round((suma_p / PESO_TOTAL_PROTECCION) * 100, 1)

    # Balance de riesgo: la vulnerabilidad amortiguada por los factores protectores
    riesgo = round(max(0.0, ivp - (0.5 * ifp)), 1)

    if riesgo < 20:
        prioridad = "Bajo"
    elif riesgo < 45:
        prioridad = "Moderado"
    elif riesgo < 70:
        prioridad = "Alto"
    else:
        prioridad = "Crítico"

    return ivp, ifp, riesgo, prioridad


@st.dialog("📋 Ficha Integral del Taller Comunitario")
def mostrar_modal_taller(taller):
    st.markdown(f"### {taller['icono']} {taller['titulo']}")
    st.markdown(f"**Público Destinatario:** `{taller.get('publico_objetivo', 'Comunidad en General')}`")

    col_m1, col_m2 = st.columns([1.1, 1.0])
    with col_m1:
        st.markdown(f"**Categoría:** `{taller['categoria']}`")
        st.markdown(f"**📍 Sede:** {taller['lugar']}")
    with col_m2:
        st.markdown(f"**🕒 Día y Horario:** **{taller['horario']}**")
        st.markdown(f"**⏱️ Frecuencia:** {taller['frecuencia']}")

    st.markdown("---")
    if taller.get("imagen_url"):
        st.image(taller["imagen_url"], caption=f"Actividad comunitaria · {taller['titulo']}", width="stretch")

    st.markdown("##### 🎯 Propósito y Descripción Integral")
    st.write(taller['detalle_ampliado'])

    st.markdown("##### 🤝 Situaciones Comunitarias a las que Responde")
    badges_html = " ".join([f"<span class='badge-prioridad-alta'>{f}</span>" for f in taller['responde_a']])
    st.markdown(badges_html, unsafe_allow_html=True)

    st.markdown("##### 👩‍⚕️ Coordinación Profesional Responsable")
    st.info(f"**A cargo de:** {taller['coordinacion']}")

    st.markdown("##### 📌 Requisitos de Asistencia")
    st.success(taller['requisitos'])

    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🙋 Me interesa participar / Asistir", key=f"modal_btn_int_{taller['id']}", width="stretch", type="primary"):
            nuevos = db.incrementar_interes_taller(taller['id'])
            st.toast(f"¡Excelente registro! Ya son {nuevos} personas interesadas en este taller. ¡Te esperamos en {taller['horario']}!")
    with col_b2:
        st.link_button("📲 Consultar al CiC Gianotti por WhatsApp", "https://wa.me/5493430000000", width="stretch")


# ===============================================================================================
# BARRA LATERAL: NAVEGACIÓN Y CONFIGURACIÓN INSTITUCIONAL
# ===============================================================================================
with st.sidebar:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4RBOC8dblkturvp2rovIlfgiCapVEZJRDC8rl6u-faw&s=10", width=190)
    st.title("RELEVAR")
    st.caption("Plataforma de Trazabilidad Sanitaria & Talleres")
    st.markdown("**FIUNER & CiC Dr. Luis Gianotti**")
    st.markdown("<small>Oro Verde · Entre Ríos · Argentina</small>", unsafe_allow_html=True)
    st.markdown("---")

    menu_seleccion = st.radio(
        "Navegación del Sistema:",
        [
            "🌱 Talleres Comunitarios & Prevención",
            "📝 Formulario de Relevamiento RELEVAR",
            "📊 Trazabilidad & Tablero Epidemiológico",
            "🚀 Gestión de Talleres & Nuevos Abordajes",
            "📑 Fundamentación Académica & Equipo"
        ],
        index=0
    )

    st.markdown("---")
    with st.expander("ℹ️ Acerca de esta Plataforma"):
        st.caption(
            "Desarrollada para la cátedra **Introducción a los Sistemas de Salud** "
            "(Bioingeniería - FIUNER) en articulación territorial con el **CiC Luis Gianotti**. "
            "Implementa el relevamiento ponderado de la 'Planilla de Agentes Sanitarios' y "
            "la gestión inteligente de talleres según la perspectiva biopsicosocial."
        )

    st.caption("🔒 *Conformidad estricta con la Ley 25.326 de Protección de Datos Personales.*")


# ===============================================================================================
# VISTA 1: TALLERES COMUNITARIOS & PREVENCIÓN (Para Visitantes / Estudiantes / Vecinos)
# ===============================================================================================
if menu_seleccion == "🌱 Talleres Comunitarios & Prevención":
    st.markdown("""
    <div class="main-header">
        <span class="subtag-header">Salud Comunitaria & Promoción de la Salud</span>
        <h1>🌱 Talleres de Prevención y Acompañamiento</h1>
        <p>
            Plataforma de articulación entre el <b>Centro de Atención Primaria CiC Dr. Luis Gianotti</b> 
            y la <b>Facultad de Ingeniería (FIUNER)</b>. Descubrí los talleres gratuitos, presenciales 
            y abiertos para estudiantes y vecinos de Oro Verde.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. CARRUSEL INTERACTIVO DE TALLERES DESTACADOS
    talleres_todos = db.obtener_todos_los_talleres(estado_filtro="Activo")
    talleres_carrusel = [t for t in talleres_todos if t.get("destacado_carrusel")]

    if not talleres_carrusel:
        talleres_carrusel = talleres_todos[:3]

    if "carrusel_idx" not in st.session_state:
        st.session_state.carrusel_idx = 0

    if talleres_carrusel:
        idx_act = st.session_state.carrusel_idx % len(talleres_carrusel)
        t_dest = talleres_carrusel[idx_act]

        c_tit, c_nav = st.columns([3, 1.2], vertical_alignment="center")
        with c_tit:
            st.markdown(f"#### 🌟 Taller Destacado ({idx_act + 1}/{len(talleres_carrusel)}): *{t_dest['titulo']}*")
        with c_nav:
            p_prev, p_ind, p_next = st.columns([1, 2, 1], vertical_alignment="center")
            with p_prev:
                if st.button("◀", key="btn_prev_carr", width="stretch", help="Anterior"):
                    st.session_state.carrusel_idx = (idx_act - 1) % len(talleres_carrusel)
                    st.rerun()
            with p_ind:
                st.markdown(f"<p style='text-align:center; font-weight:700; margin:0;'>{idx_act + 1} / {len(talleres_carrusel)}</p>", unsafe_allow_html=True)
            with p_next:
                if st.button("▶", key="btn_next_carr", width="stretch", help="Siguiente"):
                    st.session_state.carrusel_idx = (idx_act + 1) % len(talleres_carrusel)
                    st.rerun()

        # Hero Banner
        st.markdown("""<div class="carrusel-hero">""", unsafe_allow_html=True)
        col_img, col_info = st.columns([1.1, 1.7], gap="large")
        with col_img:
            if t_dest.get("imagen_url"):
                st.image(t_dest["imagen_url"], caption=f"{t_dest['lugar']} · {t_dest['horario']}", width="stretch")
            st.caption(f"👥 **Público:** {t_dest.get('publico_objetivo', 'Abierto a la comunidad')}")

        with col_info:
            st.markdown(f"<span class='badge-prioridad-alta'>{t_dest['categoria']}</span>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='font-size: 1.6rem; color: #0e4d64; margin: 0.3rem 0 0.5rem 0;'>{t_dest['icono']} {t_dest['titulo']}</h2>", unsafe_allow_html=True)
            st.write(t_dest['descripcion'])
            st.markdown(f"**📍 Sede y Horario:** `{t_dest['lugar']}` &nbsp;|&nbsp; 🕒 **{t_dest['horario']}** ({t_dest['frecuencia']})")
            st.markdown(f"**👩‍⚕️ Coordinación:** {t_dest['coordinacion']}")
            st.markdown(f"**🤝 Responde a:** " + ", ".join([f"`{f}`" for f in t_dest['responde_a'][:3]]))

            st.write("")
            c_det_btn, c_int_btn = st.columns([1.5, 1])
            with c_det_btn:
                if st.button("🔍 Ver Ficha Completa del Taller", key=f"btn_carr_ficha_{t_dest['id']}", type="primary", width="stretch"):
                    mostrar_modal_taller(t_dest)
            with c_int_btn:
                st.link_button("📲 Consultar al CIC", "https://wa.me/5493430000000", width="stretch")

        st.markdown("""</div>""", unsafe_allow_html=True)

    # 2. FILTRADO INTELIGENTE DE TALLERES POR FACTORES Y PÚBLICO
    st.markdown("---")
    st.subheader("🎯 Encontrá los talleres diseñados para tu situación")
    st.markdown("Filtrá por tus condiciones de salud o vivencias para descubrir los espacios más pertinentes:")

    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        factores_disponibles = list(FACTORES_VULNERABILIDAD_PONDERADOS.keys())
        seleccion_factores = st.multiselect(
            "Seleccioná situaciones que te preocupen o afecten a tu entorno:",
            options=factores_disponibles,
            placeholder="Ejemplo: Estrés académico, Insomnio, Mala nutrición, Vacunación..."
        )
    with f_col2:
        filtro_publico = st.selectbox(
            "Filtrar por grupo destinatario:",
            ["Todos", "Estudiantes Universitarios (FIUNER)", "Comunidad de Oro Verde / Familias"],
            index=0
        )

    # Aplicación de filtros
    talleres_visibles = talleres_todos
    if filtro_publico == "Estudiantes Universitarios (FIUNER)":
        talleres_visibles = [t for t in talleres_visibles if "Estudiante" in t.get("publico_objetivo", "") or "FIUNER" in t.get("publico_objetivo", "")]
    elif filtro_publico == "Comunidad de Oro Verde / Familias":
        talleres_visibles = [t for t in talleres_visibles if "Estudiante" not in t.get("publico_objetivo", "")]

    if seleccion_factores:
        set_sel = set(seleccion_factores)
        talleres_visibles = [
            t for t in talleres_visibles 
            if any(f in set_sel for f in t.get("responde_a", []))
        ]
        if not talleres_visibles:
            st.info("ℹ️ No hay talleres exclusivos con esa combinación exacta; te mostramos todos los talleres activos disponibles:")
            talleres_visibles = talleres_todos

    st.markdown(f"##### Mostrando **{len(talleres_visibles)}** talleres disponibles:")

    # 3. GRILLA DE TALLERES
    cols_grid = st.columns(3)
    for i, t in enumerate(talleres_visibles):
        col_dest = cols_grid[i % 3]
        with col_dest:
            responde_str = ", ".join(t.get("responde_a", [])[:2])
            st.markdown(f"""
            <div class="taller-card">
                <div>
                    <span class="badge-prioridad-moderada">{t['categoria']}</span>
                    <div class="taller-titulo">{t['icono']} {t['titulo']}</div>
                    <div class="taller-desc">{t['descripcion']}</div>
                    <div class="taller-responde">
                        <b>Aborda:</b> {responde_str}...
                    </div>
                </div>
                <div class="taller-lugar-horario">
                    📍 {t['lugar']}<br>
                    🕒 {t['horario']} ({t['frecuencia']})
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📋 Ver Información y Horarios", key=f"btn_ver_grid_{t['id']}", width="stretch"):
                mostrar_modal_taller(t)
            st.write("")

    # 4. CENTROS DE SALUD DE REFERENCIA EN ORO VERDE
    st.markdown("---")
    st.subheader("🏥 Red de Efectores de Salud en la Comunidad")
    st.markdown("El proyecto toma como eje central el **Centro Integrador Comunitario Dr. Luis Gianotti**:")

    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        st.markdown("""
        <div class="centro-card-activo">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="margin:0; color:#0e4d64; font-size:1.25rem;">CiC "Luis Gianotti"</h3>
                <span class="badge-prioridad-baja">Sede Central</span>
            </div>
            <p style="color:#0891b2; font-size:0.85rem; margin:0.2rem 0 0.5rem 0;">Av. Los Chañares y calle Las Golondrinas</p>
            <div class="centro-item-stat"><span>Población asignada</span><b>11.200</b></div>
            <div class="centro-item-stat"><span>Consultas anuales</span><b>42.300</b></div>
            <div class="centro-item-stat"><span>Especialidades activas</span><b>8 servicios</b></div>
            <div style="margin-top:0.8rem; text-align:center; color:#0e4d64; font-size:0.82rem; font-weight:700; background:#e0f2fe; padding:6px; border-radius:6px;">
                ✅ Sede de talleres y relevamiento RELEVAR
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_e2:
        st.markdown("""
        <div class="centro-card">
            <h3 style="margin-top:0; color:#1e293b; font-size:1.2rem;">CAPS "Santa Lucía"</h3>
            <p style="color:#64748b; font-size:0.85rem;">Atención barrial y medicina general</p>
            <div class="centro-item-stat"><span>Población asignada</span><b>8.400</b></div>
            <div class="centro-item-stat"><span>Consultas anuales</span><b>31.500</b></div>
            <div class="centro-item-stat"><span>Equipo profesional</span><b>14</b></div>
        </div>
        """, unsafe_allow_html=True)

    with col_e3:
        st.markdown("""
        <div class="centro-card">
            <h3 style="margin-top:0; color:#1e293b; font-size:1.2rem;">CAPS "Jorge Newbery"</h3>
            <p style="color:#64748b; font-size:0.85rem;">Enfermería, clínica médica y vacunas</p>
            <div class="centro-item-stat"><span>Población asignada</span><b>6.900</b></div>
            <div class="centro-item-stat"><span>Consultas anuales</span><b>24.800</b></div>
            <div class="centro-item-stat"><span>Equipo profesional</span><b>11</b></div>
        </div>
        """, unsafe_allow_html=True)


# ===============================================================================================
# VISTA 2: FORMULARIO DE RELEVAMIENTO RELEVAR (Planilla de Agentes Sanitarios Ponderada)
# ===============================================================================================
elif menu_seleccion == "📝 Formulario de Relevamiento RELEVAR":
    st.markdown("""
    <div class="main-header">
        <span class="subtag-header">Instrumento Metodológico · Plataforma RELEVAR</span>
        <h1>📝 Planilla de Relevamiento de Agentes Sanitarios</h1>
        <p>
            Relevamiento epidemiológico de <b>Factores de Vulnerabilidad</b> y <b>Factores Protectores</b>. 
            Prueba piloto implementada para la comunidad estudiantil de <b>FIUNER</b> y los vecinos de <b>Oro Verde</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box-legal">
        🔒 <b>Relevamiento 100% Anónimo y Confidencial:</b> No solicitamos tu nombre ni DNI. 
        Tus respuestas se integran de forma ponderada para orientar talleres de prevención y políticas del Centro de Salud, 
        bajo estricto cumplimiento de la <b>Ley Nacional 25.326 de Protección de los Datos Personales</b>.
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_relevar_completo", clear_on_submit=False):
        st.subheader("1. Ámbito de Relevamiento y Perfil Comunitario")
        c_pop1, c_pop2 = st.columns(2)
        with c_pop1:
            tipo_poblacion_input = st.radio(
                "¿A qué grupo pertenecés? (*)",
                [
                    "Estudiante Universitario (FIUNER - Prueba Piloto)",
                    "Comunidad General (Oro Verde / Familias)"
                ],
                index=0
            )

        with c_pop2:
            rango_edad = st.selectbox(
                "Rango etario:",
                ["18 a 21 años", "22 a 25 años", "26 a 30 años", "31 a 50 años", "Más de 50 años"],
                index=1
            )

        # Campos contextuales según población
        col_carr, col_ano, col_hab = st.columns(3)
        if "FIUNER" in tipo_poblacion_input:
            with col_carr:
                carrera_input = st.selectbox("Carrera en FIUNER:", CARRERAS_FIUNER, index=0)
            with col_ano:
                ano_input = st.selectbox("Año de cursado:", ANOS_CURSADO, index=2)
            with col_hab:
                habitacional_input = st.selectbox(
                    "Situación habitacional en Oro Verde:",
                    [
                        "Alquila solo/a (lejos de familia)",
                        "Alquila con compañeros de estudio",
                        "Vive en residencia estudiantil",
                        "Vive con su familia en Oro Verde",
                        "Viaja diariamente desde Paraná u otra localidad"
                    ],
                    index=1
                )
            barrio_input = st.selectbox("Condición / Procedencia:", ZONAS_RESIDENCIA, index=1)
        else:
            carrera_input = None
            ano_input = None
            with col_carr:
                habitacional_input = st.selectbox(
                    "Tipo de vivienda:",
                    ["Vivienda propia", "Alquila", "Vivienda prestada/familiar", "Casilla/Espacio compartido"],
                    index=0
                )
            with col_ano:
                genero_input = st.selectbox("Identidad de género:", ["Femenino", "Masculino", "No binario", "Prefiero no decir"], index=0)
            with col_hab:
                barrio_input = st.selectbox("Condición / Procedencia:", ZONAS_RESIDENCIA, index=0)

        st.markdown("---")
        # -------------------------------------------------------------
        # BLOQUE 1: FACTORES DE VULNERABILIDAD
        # -------------------------------------------------------------
        st.subheader("2. Bloque: Factores de Vulnerabilidad (Biopsicosociales)")
        st.markdown(
            "Tildá las condiciones que se presenten actualmente en tu persona o en tu hogar. "
            "Cada factor cuenta con una ponderación epidemiológica para dimensionar la prioridad sanitaria:"
        )

        col_v1, col_v2 = st.columns(2)
        factores_vulnerabilidad_seleccionados = []

        todos_factores_v = list(FACTORES_VULNERABILIDAD_PONDERADOS.items())
        mitad_v = len(todos_factores_v) // 2

        with col_v1:
            st.markdown("##### 🧠 Carga Cognitiva, Estrés y Salud Mental")
            for factor_nombre, meta in todos_factores_v[:mitad_v]:
                checked = st.checkbox(
                    f"**{factor_nombre}**",
                    help=f"{meta['descripcion']} · Ponderación de riesgo: {meta['peso']} pts",
                    key=f"chk_v_{factor_nombre}"
                )
                if checked:
                    factores_vulnerabilidad_seleccionados.append(factor_nombre)

        with col_v2:
            st.markdown("##### 🩺 Salud Física, Hábitat y Cuidados")
            for factor_nombre, meta in todos_factores_v[mitad_v:]:
                checked = st.checkbox(
                    f"**{factor_nombre}**",
                    help=f"{meta['descripcion']} · Ponderación de riesgo: {meta['peso']} pts",
                    key=f"chk_v_{factor_nombre}"
                )
                if checked:
                    factores_vulnerabilidad_seleccionados.append(factor_nombre)

        st.markdown("---")
        # -------------------------------------------------------------
        # BLOQUE 2: FACTORES PROTECTORES
        # -------------------------------------------------------------
        st.subheader("3. Bloque: Factores Protectores y Redes de Apoyo")
        st.markdown(
            "Los factores protectores son recursos internos, afectivos y comunitarios que amortiguan "
            "el impacto del estrés y favorecen la resiliencia en la salud:"
        )

        col_p1, col_p2 = st.columns(2)
        factores_protectores_seleccionados = []

        todos_factores_p = list(FACTORES_PROTECTORES_PONDERADOS.items())
        mitad_p = len(todos_factores_p) // 2

        with col_p1:
            for factor_nombre, meta in todos_factores_p[:mitad_p]:
                checked_p = st.checkbox(
                    f"**{factor_nombre}**",
                    help=f"{meta['descripcion']} · Aporte protector: {meta['peso']} pts",
                    key=f"chk_p_{factor_nombre}"
                )
                if checked_p:
                    factores_protectores_seleccionados.append(factor_nombre)

        with col_p2:
            for factor_nombre, meta in todos_factores_p[mitad_p:]:
                checked_p = st.checkbox(
                    f"**{factor_nombre}**",
                    help=f"{meta['descripcion']} · Aporte protector: {meta['peso']} pts",
                    key=f"chk_p_{factor_nombre}"
                )
                if checked_p:
                    factores_protectores_seleccionados.append(factor_nombre)

        st.markdown("---")
        # -------------------------------------------------------------
        # BLOQUE 3: OBSERVACIONES O VIVENCIA EN LENGUAJE NATURAL
        # -------------------------------------------------------------
        st.subheader("4. Vivencia Personal o Aporte Libre (Opcional)")
        st.caption("Podés contarnos con tus palabras cómo sentís tu bienestar o qué talleres sentís que faltan en Oro Verde:")
        relato_libre = st.text_area(
            "Comentario o relato sobre tu salud biopsicosocial en la vida universitaria o comunitaria:",
            placeholder="Ejemplo: La época de exámenes me genera mucho estrés y contracturas. Me cuesta dormir y no conozco espacios para relajarme...",
            height=100
        )

        enviar_relevamiento = st.form_submit_button(
            "🚀 Registrar Relevamiento y Obtener Diagnóstico Ponderado",
            type="primary",
            width="stretch"
        )

    if enviar_relevamiento:
        with st.spinner("Procesando datos ponderados según el modelo epidemiológico RELEVAR..."):
            ivp, ifp, riesgo, prioridad = calcular_indices_sanitarios(
                factores_vulnerabilidad_seleccionados,
                factores_protectores_seleccionados
            )

            id_nuevo = db.registrar_relevamiento_relevar(
                tipo_poblacion=tipo_poblacion_input,
                rango_etario=rango_edad,
                genero="No especificado",
                barrio_o_residencia=barrio_input,
                carrera=carrera_input,
                ano_cursado=ano_input,
                situacion_habitacional=habitacional_input,
                factores_vulnerabilidad=factores_vulnerabilidad_seleccionados,
                factores_protectores=factores_protectores_seleccionados,
                puntaje_vulnerabilidad=ivp,
                puntaje_proteccion=ifp,
                indice_riesgo_ponderado=riesgo,
                nivel_prioridad=prioridad,
                observaciones_libres=relato_libre,
                canal="Formulario RELEVAR Web"
            )

        st.balloons()
        st.success(f"✅ ¡Relevamiento registrado con éxito en la base de datos sanitaria! Identificador: **#REL-{id_nuevo:04d}**")

        # DEVOLUCIÓN SANITARIA INMEDIATA AL USUARIO
        st.markdown("### 📊 Devolución de tu Balance Biopsicosocial:")

        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1:
            st.metric("Índice de Vulnerabilidad (IVP)", f"{ivp}%", help="Porcentaje ponderado de factores de riesgo presentes.")
        with r_col2:
            st.metric("Índice de Protección (IFP)", f"{ifp}%", help="Porcentaje ponderado de factores protectores presentes.")
        with r_col3:
            st.metric("Índice de Riesgo Sanitario", f"{riesgo} pts", help="Vulnerabilidad amortiguada por redes de protección.")
        with r_col4:
            badge_class = {
                "Bajo": "badge-prioridad-baja",
                "Moderado": "badge-prioridad-moderada",
                "Alto": "badge-prioridad-alta",
                "Crítico": "badge-prioridad-critica"
            }.get(prioridad, "badge-prioridad-moderada")
            st.markdown(f"**Semáforo de Abordaje:**<br><span class='{badge_class}' style='font-size:1.1rem;'>{prioridad}</span>", unsafe_allow_html=True)

        # RECOMENDACIÓN DE TALLERES A MEDIDA SEGÚN LO RELEVADO
        st.markdown("---")
        st.markdown("#### 🎯 Talleres Recomendados Personalizados para Vos:")
        
        todos_t = db.obtener_todos_los_talleres(estado_filtro="Activo")
        recomendados = []
        for t in todos_t:
            coincidencias = [f for f in factores_vulnerabilidad_seleccionados if f in t.get("responde_a", [])]
            if coincidencias:
                recomendados.append((t, len(coincidencias)))

        recomendados.sort(key=lambda x: x[1], reverse=True)

        if recomendados:
            st.write(f"Encontramos **{len(recomendados)}** talleres en el CiC Gianotti y FIUNER que abordan directamente tus factores marcados:")
            c_rec = st.columns(min(3, len(recomendados)))
            for idx, (t_rec, cant) in enumerate(recomendados[:3]):
                with c_rec[idx]:
                    st.markdown(f"""
                    <div class="taller-card">
                        <div>
                            <span class="badge-prioridad-baja">Recomendado ({cant} coincidencia/s)</span>
                            <div class="taller-titulo">{t_rec['icono']} {t_rec['titulo']}</div>
                            <div class="taller-desc">{t_rec['descripcion']}</div>
                        </div>
                        <div class="taller-lugar-horario">
                            📍 {t_rec['lugar']}<br>
                            🕒 {t_rec['horario']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Ver Ficha de Asistencia", key=f"btn_rec_{t_rec['id']}", width="stretch"):
                        mostrar_modal_taller(t_rec)
        else:
            st.info("ℹ️ ¡Excelente balance! Tus factores protectores son sólidos. Te invitamos a conocer todos los talleres comunitarios para compartir con tus pares.")


# ===============================================================================================
# VISTA 3: TRAZABILIDAD & TABLERO EPIDEMIOLÓGICO (Indicadores de Salud)
# ===============================================================================================
elif menu_seleccion == "📊 Trazabilidad & Tablero Epidemiológico":
    st.markdown("""
    <div class="main-header">
        <span class="subtag-header">Componente 2 · Análisis Epidemiológico de Indicadores</span>
        <h1>📊 Trazabilidad y Tablero de Indicadores de la Salud</h1>
        <p>
            Vigilancia epidemiológica situacional de la comunidad de <b>Oro Verde</b> y la población universitaria de <b>FIUNER</b>. 
            Procesamiento ponderado de factores de vulnerabilidad vs factores protectores.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Botón para sembrar datos demo si la base está vacía
    relevamientos_raw = db.obtener_relevamientos_relevar()
    if len(relevamientos_raw) == 0:
        st.info("ℹ️ La base de datos de relevamientos está vacía. Podés cargar los datos iniciales de la prueba piloto FIUNER y Oro Verde:")
        if st.button("🧪 Cargar Casos Demo de la Prueba Piloto FIUNER & Oro Verde"):
            db.poblar_datos_relevar_demo()
            st.rerun()

    metricas_rel = db.obtener_metricas_relevar()

    # KPIS PRINCIPALES
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Relevamientos", metricas_rel["total"])
    with k2:
        st.metric("Prueba Piloto FIUNER", metricas_rel["fiuner_total"], delta="Estudiantes")
    with k3:
        st.metric("Comunidad Oro Verde", metricas_rel["comunidad_total"], delta="Vecinos y Familias")
    with k4:
        st.metric("Vulnerabilidad Media (IVP)", f"{metricas_rel['ivp_promedio']}%")
    with k5:
        st.metric("Afectación Salud Mental", f"{metricas_rel['salud_mental_prevalencia']}%", delta="Estrés / Ansiedad", delta_color="inverse")

    st.markdown("---")

    # FILTROS DINÁMICOS
    st.subheader("🔍 Filtros de Segmentación Poblacional")
    f_pob, f_prio, f_barrio = st.columns(3)
    with f_pob:
        filtro_poblacion = st.selectbox(
            "Filtrar por Grupo Poblacional:",
            ["Todas", "Estudiante FIUNER (Prueba Piloto)", "Comunidad General (Oro Verde / CIC)"],
            index=0
        )
    with f_prio:
        filtro_prioridad = st.selectbox(
            "Filtrar por Nivel de Prioridad Sanitaria:",
            ["Todas", "Crítico", "Alto", "Moderado", "Bajo"],
            index=0
        )
    with f_barrio:
        filtro_barrio = st.selectbox(
            "Filtrar por Condición / Procedencia:",
            ["Todos"] + ZONAS_RESIDENCIA,
            index=0
        )

    # Obtención de registros filtrados
    relevamientos_filtrados = db.obtener_relevamientos_relevar(
        filtro_poblacion=filtro_poblacion,
        filtro_prioridad=filtro_prioridad,
        filtro_barrio=filtro_barrio
    )

    df_rel = pd.DataFrame(relevamientos_filtrados)

    if not df_rel.empty:
        # GRÁFICOS EPIDEMIOLÓGICOS CON PLOTLY
        g1, g2 = st.columns(2)

        with g1:
            st.markdown("##### ⚠️ Factores de Vulnerabilidad Más Prevalentes")
            # Conteo de vulnerabilidades en el conjunto filtrado
            vuln_dict = {}
            for row_vuln in df_rel["factores_vulnerabilidad"]:
                for v in row_vuln:
                    vuln_dict[v] = vuln_dict.get(v, 0) + 1

            df_vuln = pd.DataFrame(list(vuln_dict.items()), columns=["Factor", "Casos"]).sort_values("Casos", ascending=True).tail(8)
            fig_v = px.bar(
                df_vuln,
                x="Casos",
                y="Factor",
                orientation="h",
                color="Casos",
                color_continuous_scale="Reds",
                text="Casos"
            )
            fig_v.update_layout(height=360, margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_v, width="stretch")

        with g2:
            st.markdown("##### 🛡️ Factores Protectores y Redes de Apoyo")
            prot_dict = {}
            for row_prot in df_rel["factores_protectores"]:
                for p in row_prot:
                    prot_dict[p] = prot_dict.get(p, 0) + 1

            df_prot = pd.DataFrame(list(prot_dict.items()), columns=["Factor Protector", "Frecuencia"]).sort_values("Frecuencia", ascending=True).tail(8)
            fig_p = px.bar(
                df_prot,
                x="Frecuencia",
                y="Factor Protector",
                orientation="h",
                color="Frecuencia",
                color_continuous_scale="Greens",
                text="Frecuencia"
            )
            fig_p.update_layout(height=360, margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_p, width="stretch")

        g3, g4 = st.columns(2)
        with g3:
            st.markdown("##### ⚖️ Matriz Biopsicosocial: Vulnerabilidad (IVP) vs Protección (IFP)")
            fig_scatter = px.scatter(
                df_rel,
                x="puntaje_proteccion",
                y="puntaje_vulnerabilidad",
                color="nivel_prioridad",
                size="indice_riesgo_ponderado",
                hover_data=["tipo_poblacion", "barrio_o_residencia"],
                color_discrete_map={
                    "Crítico": "#ef4444",
                    "Alto": "#f97316",
                    "Moderado": "#eab308",
                    "Bajo": "#22c55e"
                },
                labels={
                    "puntaje_proteccion": "Índice de Factores Protectores (IFP %)",
                    "puntaje_vulnerabilidad": "Índice de Vulnerabilidad Ponderada (IVP %)"
                }
            )
            fig_scatter.update_layout(height=360, margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_scatter, width="stretch")

        with g4:
            st.markdown("##### 🚦 Distribución del Semáforo de Prioridad Sanitaria")
            conteo_prio = df_rel["nivel_prioridad"].value_counts().reset_index()
            conteo_prio.columns = ["Prioridad", "Cantidad"]
            fig_donut = px.pie(
                conteo_prio,
                names="Prioridad",
                values="Cantidad",
                color="Prioridad",
                color_discrete_map={
                    "Crítico": "#ef4444",
                    "Alto": "#f97316",
                    "Moderado": "#eab308",
                    "Bajo": "#22c55e"
                },
                hole=0.45
            )
            fig_donut.update_layout(height=360, margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_donut, width="stretch")

        # TABLA DE REGISTROS ANONIMIZADOS
        st.markdown("---")
        st.subheader(f"📋 Registros Epidemiológicos Filtrados ({len(df_rel)} relevamientos)")
        
        columnas_tabla = [
            "id", "fecha_hora", "tipo_poblacion", "barrio_o_residencia",
            "puntaje_vulnerabilidad", "puntaje_proteccion", "indice_riesgo_ponderado", "nivel_prioridad"
        ]
        st.dataframe(
            df_rel[columnas_tabla].rename(columns={
                "id": "ID",
                "fecha_hora": "Fecha/Hora",
                "tipo_poblacion": "Población",
                "barrio_o_residencia": "Condición / Procedencia",
                "puntaje_vulnerabilidad": "IVP (%)",
                "puntaje_proteccion": "IFP (%)",
                "indice_riesgo_ponderado": "Riesgo Ponderado",
                "nivel_prioridad": "Semáforo"
            }),
            width="stretch",
            hide_index=True
        )

        with st.expander("🔍 Explorar Detalles y Vivencias Libres de los Relevamientos"):
            for _, r in df_rel.iterrows():
                badge_p = {
                    "Crítico": "badge-prioridad-critica",
                    "Alto": "badge-prioridad-alta",
                    "Moderado": "badge-prioridad-moderada",
                    "Bajo": "badge-prioridad-baja"
                }.get(r["nivel_prioridad"], "badge-prioridad-baja")

                st.markdown(f"""
                **Relevamiento #REL-{r['id']:04d}** | *{r['fecha_hora']}* | Población: **{r['tipo_poblacion']}**  
                Procedencia: **{r['barrio_o_residencia']}** | Prioridad: <span class="{badge_p}">{r['nivel_prioridad']}</span> (IVP: {r['puntaje_vulnerabilidad']}% | IFP: {r['puntaje_proteccion']}%)  
                **Vulnerabilidades:** {', '.join(r['factores_vulnerabilidad']) if r['factores_vulnerabilidad'] else 'Ninguna marcada'}  
                **Protectores:** {', '.join(r['factores_protectores']) if r['factores_protectores'] else 'Ninguno marcado'}  
                """, unsafe_allow_html=True)
                if r.get("observaciones_libres"):
                    st.info(f"💬 *Vivencia reportada:* \"{r['observaciones_libres']}\"")
                st.markdown("---")

    else:
        st.warning("⚠️ No se encontraron registros con los filtros seleccionados.")


# ===============================================================================================
# VISTA 4: GESTIÓN DE TALLERES & SUGERENCIAS DE NUEVOS ABORDAJES (Para Responsables del CAPS)
# ===============================================================================================
elif menu_seleccion == "🚀 Gestión de Talleres & Nuevos Abordajes":
    st.markdown("""
    <div class="main-header">
        <span class="subtag-header">Componente 3 · Criterio de Generación y Promoción de Talleres</span>
        <h1>🚀 Gestión de Talleres & Nuevos Desarrollos</h1>
        <p>
            Módulo para el <b>Equipo Directivo del CiC Luis Gianotti</b> y la <b>Cátedra de FIUNER</b>. 
            Permite evaluar demandas insatisfechas, recibir sugerencias automáticas de nuevos talleres y 
            poner en marcha nuevas propuestas de abordaje comunitario.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. MOTOR DE DETECCIÓN Y SUGERENCIA DE NUEVOS TALLERES BASADO EN LOS DATOS RELEVADOS
    st.subheader("💡 Sugerencias Automáticas de Puesta en Marcha (Basadas en Datos Sanitarios)")
    st.caption("Conforme al Objetivo 3 del proyecto, el sistema procesa la última carga de información para sugerir talleres prioritarios:")

    metricas_sug = db.obtener_metricas_relevar()
    conteo_v = metricas_sug.get("factores_vuln_conteo", {})
    talleres_existentes = db.obtener_todos_los_talleres(estado_filtro="Todos")
    titulos_existentes = [t["titulo"].lower() for t in talleres_existentes]

    # Reglas de inferencia epidemiológica para sugerir nuevos talleres
    sugerencias_nuevas = []

    if conteo_v.get("Dolores osteomusculares o cefaleas frecuentes", 0) >= 2 and not any("ergonomía" in tit or "postural" in tit for tit in titulos_existentes if "Pausas" not in tit):
        sugerencias_nuevas.append({
            "id": "sug-ergonomia-avanzada",
            "titulo": "Taller de Ergonomía y Prevención del Síndrome del Túnel Carpiano",
            "categoria": "Prevención y cuidados",
            "icono": "💻",
            "descripcion": "Corrección biomecánica de puestos de estudio y trabajo en computadoras para prevenir lesiones por esfuerzo repetitivo (RSI).",
            "detalle_ampliado": (
                "Propuesta interdisciplinaria entre Kinesiología y Bioingeniería orientada a estudiantes de informática y carreras técnicas. "
                "Incluye calibración ergonómica personalizada, ejercicios propioceptivos de muñeca y hombros, y pautas visuales para reducir fatiga ocular."
            ),
            "responde_a": ["Dolores osteomusculares o cefaleas frecuentes", "Sedentarismo o inactividad física severa"],
            "publico_objetivo": "Estudiantes y Trabajadores Informáticos",
            "lugar": "CiC 'Gianotti' / Laboratorio FIUNER",
            "horario": "Jueves · 18:30 h",
            "frecuencia": "Quincenal",
            "coordinacion": "Servicio de Kinesiología y Bioingeniería Clínica",
            "requisitos": "Abierto y gratuito."
        })

    if conteo_v.get("Aislamiento social / desarraigo familiar", 0) >= 2 and not any("desarraigo" in tit or "integración" in tit for tit in titulos_existentes):
        sugerencias_nuevas.append({
            "id": "sug-redes-pares",
            "titulo": "Encuentros de Integración y Acompañamiento del Desarraigo Estudiantil",
            "categoria": "Salud mental y bienestar",
            "icono": "🤝",
            "descripcion": "Espacio para estudiantes foráneos que viven en Oro Verde: redes de amistad, adaptación cultural y contención comunitaria.",
            "detalle_ampliado": (
                "Ronda comunitaria coordinada por Trabajo Social y Psicología del CIC. Busca combatir la soledad no deseada de jóvenes que "
                "se trasladan a Oro Verde para estudiar, propiciando actividades de integración vecinal, conocimiento del pueblo y apoyo afectivo mutuo."
            ),
            "responde_a": ["Aislamiento social / desarraigo familiar", "Episodios frecuentes de ansiedad o angustia"],
            "publico_objetivo": "Estudiantes Foráneos de FIUNER",
            "lugar": "CiC 'Gianotti' - Salón Comunitario",
            "horario": "Viernes · 19:00 h",
            "frecuencia": "Semanal",
            "coordinacion": "Trabajadoras Sociales (CIC) y Centro de Estudiantes",
            "requisitos": "Libre y gratuito. Traé mate."
        })

    if conteo_v.get("Inestabilidad económica severa / dificultad de sustento", 0) >= 2 and not any("huerta" in tit or "economía" in tit for tit in titulos_existentes):
        sugerencias_nuevas.append({
            "id": "sug-huerta-comunitaria",
            "titulo": "Huerta Agroecológica Comunitaria y Soberanía Alimentaria",
            "categoria": "Salud Comunitaria y Nutrición",
            "icono": "🌱",
            "descripcion": "Producción casera de alimentos frescos, entrega de semillas de temporada y recetas de bajo costo.",
            "detalle_ampliado": (
                "Articulación con promotores de INTA ProHuerta y el CIC Gianotti. Los participantes aprenden a cultivar en balcones o patios pequeños "
                "y reciben plantines para mejorar la calidad nutricional de la canasta familiar."
            ),
            "responde_a": ["Inestabilidad económica severa / dificultad de sustento", "Mala nutrición o salteo recurrente de comidas"],
            "publico_objetivo": "Comunidad de Oro Verde y Estudiantes",
            "lugar": "CiC 'Gianotti' - Predio al Aire Libre",
            "horario": "Sábados · 10:00 h",
            "frecuencia": "Semanal",
            "coordinacion": "Lic. en Nutrición y Voluntariado Ambiental",
            "requisitos": "Gratuito. Te llevás plantines y semillas a tu casa."
        })

    # Mostrar sugerencias
    if sugerencias_nuevas:
        for sug in sugerencias_nuevas:
            st.markdown(f"""
            <div class="suggestion-box">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; color:#854d0e;">✨ Propuesta Sugerida: {sug['icono']} {sug['titulo']}</h3>
                    <span class="badge-prioridad-alta">Alta Pertinencia Sanitaria</span>
                </div>
                <p style="margin:0.5rem 0; color:#451a03; font-size:0.95rem;">{sug['descripcion']}</p>
                <small style="color:#78350f;"><b>Fundamentación:</b> Responde a factores altamente prevalentes en el último relevamiento ({', '.join(sug['responde_a'])}).</small>
            </div>
            """, unsafe_allow_html=True)

            col_sug_act, _ = st.columns([1.5, 3])
            with col_sug_act:
                if st.button(f"🚀 Poner en Marcha: {sug['titulo'][:30]}...", key=f"btn_poner_marcha_{sug['id']}", type="primary"):
                    db.registrar_nuevo_taller(
                        id_taller=f"taller-auto-{sug['id']}",
                        titulo=sug["titulo"],
                        categoria=sug["categoria"],
                        icono=sug["icono"],
                        descripcion=sug["descripcion"],
                        detalle_ampliado=sug["detalle_ampliado"],
                        responde_a=sug["responde_a"],
                        publico_objetivo=sug["publico_objetivo"],
                        lugar=sug["lugar"],
                        horario=sug["horario"],
                        frecuencia=sug["frecuencia"],
                        coordinacion=sug["coordinacion"],
                        requisitos=sug["requisitos"],
                        estado="Activo",
                        es_ficticio=1,
                        destacado_carrusel=1,
                        imagen_url="https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=800&q=80"
                    )
                    st.toast(f"¡Taller '{sug['titulo']}' puesto en marcha exitosamente!")
                    st.rerun()
    else:
        st.success("✅ **La oferta actual de talleres cubre satisfactoriamente las demandas detectadas en los últimos relevamientos.**")

    st.markdown("---")
    # 2. ALTA MANUAL DE NUEVO TALLER COMUNITARIO
    st.subheader("➕ Diseñar y Publicar un Nuevo Taller Comunitario")
    with st.expander("📝 Formulario de Creación de Nuevo Taller (Click para abrir)"):
        with st.form("form_alta_taller", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                n_titulo = st.text_input("Título del Taller:", placeholder="Ej: Grupo de Respiración Consciente y Ansiedad")
                n_categoria = st.selectbox("Categoría:", ["Salud mental y bienestar", "Prevención y cuidados", "Salud Comunitaria y Nutrición", "Materno-infantil", "Tercera edad y autonomía"])
                n_icono = st.text_input("Emoji / Ícono representativo:", value="💡")
                n_publico = st.selectbox("Público Objetivo:", ["Comunidad en General", "Estudiantes Universitarios (FIUNER)", "Adultos Mayores", "Familias"])
            with col_t2:
                n_lugar = st.text_input("Sede / Lugar:", value="CiC 'Gianotti' - Sala Interdisciplinaria")
                n_horario = st.text_input("Día y Horario:", placeholder="Ej: Jueves · 16:00 h")
                n_frecuencia = st.text_input("Frecuencia:", value="Semanal (Duración: 1h 30m)")
                n_coordinacion = st.text_input("Equipo Profesional a cargo:", placeholder="Ej: Lic. en Psicología y Kinesiólogo")

            n_desc = st.text_area("Descripción breve (para la tarjeta):", placeholder="Resumen claro de 2 oraciones para el ciudadano...")
            n_det = st.text_area("Detalle ampliado (para la ficha completa):", placeholder="Objetivos pedagógicos, técnicas a utilizar y dinámicas de grupo...")
            n_responde = st.multiselect("Problemáticas / Factores a los que da respuesta:", options=list(FACTORES_VULNERABILIDAD_PONDERADOS.keys()))
            n_requisitos = st.text_input("Requisitos:", value="100% gratuito. Sin obra social. Asistir con ropa cómoda.")

            btn_crear_taller = st.form_submit_button("💾 Guardar y Publicar Taller en la Plataforma", type="primary")

        if btn_crear_taller:
            if not n_titulo.strip() or not n_desc.strip():
                st.error("⚠️ El título y la descripción son obligatorios.")
            else:
                nuevo_id = f"taller-custom-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                db.registrar_nuevo_taller(
                    id_taller=nuevo_id,
                    titulo=n_titulo,
                    categoria=n_categoria,
                    icono=n_icono,
                    descripcion=n_desc,
                    detalle_ampliado=n_det,
                    responde_a=n_responde,
                    publico_objetivo=n_publico,
                    lugar=n_lugar,
                    horario=n_horario,
                    frecuencia=n_frecuencia,
                    coordinacion=n_coordinacion,
                    requisitos=n_requisitos,
                    estado="Activo",
                    es_ficticio=1,
                    destacado_carrusel=0,
                    imagen_url="https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80"
                )
                st.success(f"✅ ¡Taller '{n_titulo}' publicado exitosamente en la plataforma!")
                st.rerun()

    # 3. GESTIÓN Y ESTADO DE TALLERES ACTUALES
    st.markdown("---")
    st.subheader("📋 Catálogo Institucional de Talleres (Administración)")
    df_talleres = pd.DataFrame(talleres_todos)
    if not df_talleres.empty:
        cols_gest = ["id", "titulo", "categoria", "publico_objetivo", "horario", "lugar", "interesados_contador", "estado"]
        st.dataframe(
            df_talleres[cols_gest].rename(columns={
                "id": "Código",
                "titulo": "Título",
                "categoria": "Categoría",
                "publico_objetivo": "Destinatarios",
                "horario": "Horario",
                "lugar": "Lugar",
                "interesados_contador": "Interesados / Inscritos",
                "estado": "Estado"
            }),
            width="stretch",
            hide_index=True
        )


# ===============================================================================================
# VISTA 5: FUNDAMENTACIÓN ACADÉMICA, METODOLOGÍA RELEVAR & EQUIPO DE CÁTEDRA
# ===============================================================================================
elif menu_seleccion == "📑 Fundamentación Académica & Equipo":
    st.markdown("""
    <div class="main-header">
        <span class="subtag-header">Documento de Cátedra · FIUNER · UNER</span>
        <h1>📑 Fundamentación del Proyecto & Equipo de Trabajo</h1>
        <p>
            Plataforma de trazabilidad de indicadores de la salud y gestión de talleres comunitarios 
            mediante el relevamiento de datos ponderados en la “Planilla de Relevamiento de Agentes Sanitarios” 
            utilizada por la plataforma “RELEVAR” para la comunidad de Oro Verde - Entre Ríos.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_resumen, tab_metodologia, tab_institucion, tab_autores = st.tabs([
        "📄 Resumen y Justificación",
        "🔬 Metodología RELEVAR & Modelo Ponderado",
        "🏥 Institución y Contexto Territorial",
        "👥 Equipo de Trabajo & Autores"
    ])

    with tab_resumen:
        st.markdown("""
        ### 🎯 Resumen Ejecutivo
        Es especialmente importante delimitar apropiadamente las problemáticas con las que ha de lidiar un centro de salud. 
        Por ello, es esencial el poder identificarlas, teniendo en consideración la perspectiva particular que tiene la comunidad sobre las mismas. 
        En este sentido, el proyecto aporta un marco estructurado y consistente que permite determinar ambos puntos, dándoles una **apropiada ponderación 
        para definir claramente una lista de prioridades sanitarias** y en consecuencia poder realizar el desarrollo e implementación de herramientas 
        de atención y prevención comunitaria como lo son los talleres.

        ---

        ### 💡 Justificación Territorial e Importancia
        La localización territorial del proyecto comprende la **Facultad de Ingeniería (FIUNER)** en primera instancia y luego la localidad de **Oro Verde** como segunda instancia:
        - **Prueba Piloto Acotada en FIUNER:** La deseabilidad del proyecto radica en poner en marcha un sistema de relevamiento de información sanitaria dentro de la facultad. Diagnosticamos informalmente un aumento de estrés y problemas sobre la salud mental de la comunidad universitaria que transitan día a día de manera poco perceptible debido al contexto académico.
        - **Carga Cognitiva y Emocional:** Los ciclos académicos sumados al resto de los contextos particulares pueden generar una carga cognitiva y emocional significativa para la persona, lo cual podría confluir en eventos adversos sobre su salud mental y física.
        - **Perspectiva Biopsicosocial:** Hoy se entiende a la salud desde una perspectiva integral donde el relevamiento sistemático de datos permite reconocer problemáticas ignoradas y actuar tanto para el tratamiento oportuno como para la prevención comunitaria.
        """)

    with tab_metodologia:
        st.markdown("""
        ### 🔬 Metodología: Planilla de Relevamiento de Agentes Sanitarios (RELEVAR)
        Como fuente de información e instrumentación metodológica tomamos de referencia la **“Planilla de Relevamiento de Agentes Sanitarios”** 
        utilizada en la plataforma online **“RELEVAR”**, la cual se adaptó a un formulario online y anónimo para la comunidad universitaria y los vecinos de Oro Verde.

        #### Objetivos Particulares del Sistema:
        1. **Relevar métricas sanitarias:** Formulario online adaptado de las planillas oficiales, resguardando la privacidad y anonimato.
        2. **Procesar la información y definir indicadores sanitarios de interés:** Algoritmo ponderado que calcula el Índice de Vulnerabilidad Ponderada (IVP), el Índice de Factores Protectores (IFP) y el balance de riesgo para definir prioridades sanitarias.
        3. **Elaborar propuestas de abordaje mediante talleres comunitarios específicos:** Ofrecer en la misma plataforma propuestas vigentes para usuarios visitantes y sugerencias de nuevos desarrollos y puestas en marcha para usuarios responsables del efector de salud.

        #### Modelo Matemático de Ponderación:
        $$\\text{IVP} = \\frac{\\sum (\\text{Vulnerabilidades Marcadas} \\times \\text{Peso}_i)}{\\text{Peso Máximo Vulnerabilidad}} \\times 100$$
        $$\\text{IFP} = \\frac{\\sum (\\text{Factores Protectores} \\times \\text{Peso}_j)}{\\text{Peso Máximo Protección}} \\times 100$$
        $$\\text{Índice de Riesgo} = \\max(0, \\text{IVP} - 0.5 \\times \\text{IFP})$$
        """)

    with tab_institucion:
        st.markdown("""
        ### 🏥 Centro de Atención a la Salud “Luis Gianotti” (CiC)
        - **Tipo de Institución:** Centro Integrador Comunitario (CIC) dedicado a la Atención Primaria de la Salud (APS).
        - **Fecha de Inauguración:** 12 de noviembre de 2010.
        - **Ubicación Territorial:** Av. Los Chañares y calle Las Golondrinas, Oro Verde, Entre Ríos.
        - **Especialidades y Servicios:** Clínica médica, odontología, kinesiología, ginecología, ecografía, obstetricia, pediatría, podología, enfermería y vacunatorio.
        - **Sitio Web Institucional:** [oroverde.com.ar/web/centro-integrador-comunitario/](https://www.oroverde.com.ar/web/centro-integrador-comunitario/)
        - **Vinculación Universitaria:** Articulación directa con la Cátedra de Introducción a los Sistemas de Salud de la Facultad de Ingeniería (UNER) para docencia, extensión comunitaria e informática médica.
        """)

    with tab_autores:
        st.markdown("""
        ### 👥 Equipo Autores del Proyecto (Cátedra de Introducción a los Sistemas de Salud)
        **Facultad de Ingeniería - Universidad Nacional de Entre Ríos (UNER)**
        """)

        autores = [
            "YUSTRA, Abril", "GONZALES, Malena", "LANERI, Guadalupe", "SOBRERO, Francisco",
            "ROLDAN, Mateo", "RABEY, Pedro", "CORIA, Valentín Pedro", "IURATO, Mateo",
            "HUCK, Kelien", "OBREGON, Javier", "Poro", "Samun", "Simon", "Tiziano",
            "GONZÁLEZ, Tomás", "AUDICIO GASTALDI, Marcelo Gastón"
        ]

        c_a1, c_a2 = st.columns(2)
        mitad_a = len(autores) // 2
        with c_a1:
            for a in autores[:mitad_a]:
                st.markdown(f"- 🎓 **{a}**")
        with c_a2:
            for a in autores[mitad_a:]:
                st.markdown(f"- 🎓 **{a}**")

        st.markdown("""
        ---
        **Colaboradores Institucionales:**
        - ● **Cátedra de Introducción a los Sistemas de Salud** (Bioingeniería - FIUNER)
        - ● **Efector de Salud CiC Luis Gianotti** (Oro Verde)

        **Parámetros Académicos:**
        - **Duración del Trabajo:** 2 semanas
        - **Palabras Clave:** `salud`, `prevención`, `trazabilidad`, `talleres`, `software`.
        - **Marco Legal:** Ley Nacional 25.326 de Protección de los Datos Personales (Argentina).
        """)
