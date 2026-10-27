"""
Módulo de Arquitectura de Datos y Persistencia
Sistema de Relevamiento Comunitario e Interacción Ciudadana
Centro de Atención Primaria de la Salud (CAPS) "Dr. Luis Gianotti" - Oro Verde, Entre Ríos
Asignatura: Introducción a los Sistemas de Salud - Bioingeniería (UNER)
"""

import sqlite3
import os
import json
import uuid
import re
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple

# Rutas canónicas para base de datos y archivos multimedia persistentes
DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(DIRECTORIO_RAIZ, "caps_gianotti.db")
CARPETA_UPLOADS = os.path.join(DIRECTORIO_RAIZ, "uploads")
CARPETA_INFORMES = os.path.join(CARPETA_UPLOADS, "informes")
CARPETA_CIUDADANOS = os.path.join(CARPETA_UPLOADS, "ciudadanos")

os.makedirs(CARPETA_INFORMES, exist_ok=True)
os.makedirs(CARPETA_CIUDADANOS, exist_ok=True)


def guardar_archivo_adjunto(archivo, subcarpeta: str = "informes") -> str:
    """
    Guarda un archivo multimedia subido en el sistema de archivos local
    y retorna la ruta relativa normalizada para su persistencia en BD y despliegue en web.
    """
    carpeta_destino = os.path.join(CARPETA_UPLOADS, subcarpeta)
    os.makedirs(carpeta_destino, exist_ok=True)

    # Sanitización de nombre original
    nombre_limpio = re.sub(r'[^a-zA-Z0-9_.-]', '_', archivo.name)
    nombre_seguro = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}_{nombre_limpio}"
    ruta_absoluta = os.path.join(carpeta_destino, nombre_seguro)

    with open(ruta_absoluta, "wb") as f:
        f.write(archivo.getbuffer())

    ruta_relativa = os.path.relpath(ruta_absoluta, DIRECTORIO_RAIZ).replace("\\", "/")
    return ruta_relativa


def obtener_conexion() -> sqlite3.Connection:
    """
    Establece y configura la conexión con la base de datos SQLite local.
    Habilita el modo WAL (Write-Ahead Logging) y timeout extendido para
    garantizar concurrencia segura ante múltiples peticiones simultáneas.
    """
    conexion = sqlite3.connect(RUTA_BD, timeout=30.0, check_same_thread=False)
    conexion.row_factory = sqlite3.Row
    # Optimizaciones de concurrencia e integridad referencial
    conexion.execute("PRAGMA journal_mode = WAL;")
    conexion.execute("PRAGMA synchronous = NORMAL;")
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion


def inicializar_base_datos() -> None:
    """
    Crea las tablas e índices necesarios para el relevamiento poblacional
    e informes institucionales si aún no existen en el archivo SQLite local.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        
        # Tabla principal: Relevamiento_Poblacional
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Relevamiento_Poblacional (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                edad INTEGER NULL,
                barrio TEXT NULL,
                relato_ciudadano TEXT NOT NULL,
                canal_ingreso TEXT DEFAULT 'Portal Web Movil',
                categoria_ia TEXT DEFAULT 'Pendiente de Clasificación',
                sentimiento_ia TEXT DEFAULT 'Pendiente',
                urgencia_ia TEXT DEFAULT 'Pendiente',
                resumen_ia TEXT NULL,
                procesado_ia INTEGER DEFAULT 0,
                fecha_procesamiento DATETIME NULL,
                estado_gestion TEXT DEFAULT 'Abierto',
                ruta_imagen TEXT NULL
            );
        """)
        
        # Índices para optimizar consultas agregadas y filtros del tablero
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relevamiento_fecha 
            ON Relevamiento_Poblacional(fecha_hora);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relevamiento_urgencia 
            ON Relevamiento_Poblacional(urgencia_ia);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relevamiento_categoria 
            ON Relevamiento_Poblacional(categoria_ia);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relevamiento_barrio 
            ON Relevamiento_Poblacional(barrio);
        """)

        # Migración segura para bases de datos existentes: asegurar columna ruta_imagen
        try:
            cursor.execute("ALTER TABLE Relevamiento_Poblacional ADD COLUMN ruta_imagen TEXT NULL;")
        except sqlite3.OperationalError:
            pass

        # Tabla de Informes Sanitarios y Auditorías Técnicas del CAPS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Informes_Sanitarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_informe DATE NOT NULL,
                titulo TEXT NOT NULL,
                tipo_informe TEXT NOT NULL,
                area_servicio TEXT NOT NULL,
                autor TEXT NOT NULL,
                prioridad TEXT DEFAULT 'Media',
                estado TEXT DEFAULT 'Aprobado',
                resumen TEXT NOT NULL,
                contenido TEXT NOT NULL,
                recomendaciones TEXT NULL,
                rutas_imagenes TEXT NULL
            );
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_informes_fecha 
            ON Informes_Sanitarios(fecha_informe);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_informes_tipo 
            ON Informes_Sanitarios(tipo_informe);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_informes_area 
            ON Informes_Sanitarios(area_servicio);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_informes_prioridad 
            ON Informes_Sanitarios(prioridad);
        """)

        # Tabla RELEVAR: Planilla de Relevamiento de Agentes Sanitarios (Factores Ponderados)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Relevamiento_Relevar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo_poblacion TEXT NOT NULL,
                rango_etario TEXT NULL,
                genero TEXT NULL,
                barrio_o_residencia TEXT NULL,
                carrera TEXT NULL,
                ano_cursado TEXT NULL,
                situacion_habitacional TEXT NULL,
                factores_vulnerabilidad TEXT NOT NULL,
                factores_protectores TEXT NOT NULL,
                puntaje_vulnerabilidad REAL NOT NULL,
                puntaje_proteccion REAL NOT NULL,
                indice_riesgo_ponderado REAL NOT NULL,
                nivel_prioridad TEXT NOT NULL,
                observaciones_libres TEXT NULL,
                canal TEXT DEFAULT 'Formulario RELEVAR Web'
            );
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relevar_fecha 
            ON Relevamiento_Relevar(fecha_hora);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relevar_poblacion 
            ON Relevamiento_Relevar(tipo_poblacion);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relevar_prioridad 
            ON Relevamiento_Relevar(nivel_prioridad);
        """)

        # Tabla de Talleres Comunitarios del Sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Talleres_Sistema (
                id TEXT PRIMARY KEY,
                titulo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                icono TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                detalle_ampliado TEXT NOT NULL,
                responde_a TEXT NOT NULL,
                publico_objetivo TEXT DEFAULT 'Todos',
                lugar TEXT NOT NULL,
                horario TEXT NOT NULL,
                frecuencia TEXT NOT NULL,
                coordinacion TEXT NOT NULL,
                requisitos TEXT NOT NULL,
                estado TEXT DEFAULT 'Activo',
                es_ficticio INTEGER DEFAULT 0,
                destacado_carrusel INTEGER DEFAULT 0,
                imagen_url TEXT NULL,
                interesados_contador INTEGER DEFAULT 0,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conexion.commit()


def registrar_reclamo_ciudadano(
    relato: str,
    edad: Optional[int] = None,
    barrio: Optional[str] = None,
    canal: str = "Portal Web Movil",
    ruta_imagen: Optional[str] = None
) -> int:
    """
    Registra un nuevo relato comunitario de un vecino de Oro Verde.
    Permite opcionalmente adjuntar una imagen de comprobante o evidencia.
    Retorna el ID autoincremental generado.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Relevamiento_Poblacional (
                fecha_hora, edad, barrio, relato_ciudadano, canal_ingreso, procesado_ia, ruta_imagen
            ) VALUES (
                ?, ?, ?, ?, ?, 0, ?
            );
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            edad if (edad is not None and edad > 0) else None,
            barrio.strip() if (barrio and barrio.strip()) else "No especificado",
            relato.strip(),
            canal,
            ruta_imagen
        ))
        conexion.commit()
        return cursor.lastrowid


def actualizar_resultado_triaje_ia(
    reporte_id: int,
    categoria: str,
    sentimiento: str,
    urgencia: str,
    resumen: str
) -> bool:
    """
    Actualiza el registro con las conclusiones del procesamiento de lenguaje natural
    realizado por el modelo local Ollama.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE Relevamiento_Poblacional
            SET 
                categoria_ia = ?,
                sentimiento_ia = ?,
                urgencia_ia = ?,
                resumen_ia = ?,
                procesado_ia = 1,
                fecha_procesamiento = ?
            WHERE id = ?;
        """, (
            categoria,
            sentimiento,
            urgencia,
            resumen,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            reporte_id
        ))
        conexion.commit()
        return cursor.rowcount > 0


def obtener_todos_los_reportes(
    filtro_categoria: Optional[str] = None,
    filtro_urgencia: Optional[str] = None,
    filtro_barrio: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Recupera los reportes ciudadanos almacenados, aplicando filtros opcionales
    para el Tablero de Gestión Institucional.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        
        query = "SELECT * FROM Relevamiento_Poblacional WHERE 1=1"
        parametros = []
        
        if filtro_categoria and filtro_categoria != "Todas":
            query += " AND categoria_ia = ?"
            parametros.append(filtro_categoria)
            
        if filtro_urgencia and filtro_urgencia != "Todas":
            query += " AND urgencia_ia = ?"
            parametros.append(filtro_urgencia)
            
        if filtro_barrio and filtro_barrio != "Todos":
            query += " AND barrio = ?"
            parametros.append(filtro_barrio)
            
        if fecha_desde:
            query += " AND date(fecha_hora) >= date(?)"
            parametros.append(fecha_desde)
            
        if fecha_hasta:
            query += " AND date(fecha_hora) <= date(?)"
            parametros.append(fecha_hasta)
            
        query += " ORDER BY fecha_hora DESC;"
        
        cursor.execute(query, parametros)
        filas = cursor.fetchall()
        return [dict(fila) for fila in filas]


def obtener_metricas_epidemiologicas() -> Dict[str, Any]:
    """
    Calcula agregaciones e indicadores situacionales clave para la toma
    de decisiones en la dirección del CAPS Luis Gianotti.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        
        # Total de reportes
        cursor.execute("SELECT COUNT(*) AS total FROM Relevamiento_Poblacional;")
        total_reportes = cursor.fetchone()["total"]
        
        # Reportes pendientes vs procesados por IA
        cursor.execute("SELECT COUNT(*) AS procesados FROM Relevamiento_Poblacional WHERE procesado_ia = 1;")
        procesados = cursor.fetchone()["procesados"]
        
        # Distribución de urgencia
        cursor.execute("""
            SELECT urgencia_ia, COUNT(*) as cantidad 
            FROM Relevamiento_Poblacional 
            GROUP BY urgencia_ia;
        """)
        urgencias = {row["urgencia_ia"]: row["cantidad"] for row in cursor.fetchall()}
        
        # Distribución de categorías
        cursor.execute("""
            SELECT categoria_ia, COUNT(*) as cantidad 
            FROM Relevamiento_Poblacional 
            GROUP BY categoria_ia 
            ORDER BY cantidad DESC;
        """)
        categorias = {row["categoria_ia"]: row["cantidad"] for row in cursor.fetchall()}
        
        # Distribución de sentimiento
        cursor.execute("""
            SELECT sentimiento_ia, COUNT(*) as cantidad 
            FROM Relevamiento_Poblacional 
            GROUP BY sentimiento_ia;
        """)
        sentimientos = {row["sentimiento_ia"]: row["cantidad"] for row in cursor.fetchall()}
        
        # Casos críticos no resueltos
        cursor.execute("""
            SELECT COUNT(*) as criticos 
            FROM Relevamiento_Poblacional 
            WHERE urgencia_ia IN ('Crítica/Inmediata', 'Alta');
        """)
        criticos = cursor.fetchone()["criticos"]
        
        return {
            "total_reportes": total_reportes,
            "procesados_ia": procesados,
            "pendientes_ia": total_reportes - procesados,
            "distribucion_urgencias": urgencias,
            "distribucion_categorias": categorias,
            "distribucion_sentimientos": sentimientos,
            "casos_alta_criticidad": criticos
        }


# =====================================================================
# GESTIÓN Y PERSISTENCIA DE INFORMES INSTITUCIONALES Y TÉCNICOS
# =====================================================================

def registrar_informe_sanitario(
    titulo: str,
    fecha_informe: str,
    tipo_informe: str,
    area_servicio: str,
    autor: str,
    prioridad: str,
    estado: str,
    resumen: str,
    contenido: str,
    recomendaciones: Optional[str] = None,
    rutas_imagenes: Optional[List[str]] = None
) -> int:
    """
    Registra un nuevo informe técnico o médico institucional con imágenes adjuntas opcionales.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        rutas_json = json.dumps(rutas_imagenes if rutas_imagenes else [], ensure_ascii=False)
        cursor.execute("""
            INSERT INTO Informes_Sanitarios (
                fecha_registro, fecha_informe, titulo, tipo_informe, area_servicio,
                autor, prioridad, estado, resumen, contenido, recomendaciones, rutas_imagenes
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            );
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            fecha_informe,
            titulo.strip(),
            tipo_informe,
            area_servicio,
            autor.strip(),
            prioridad,
            estado,
            resumen.strip(),
            contenido.strip(),
            recomendaciones.strip() if recomendaciones else None,
            rutas_json
        ))
        conexion.commit()
        return cursor.lastrowid


def obtener_todos_los_informes(
    filtro_tipo: Optional[str] = None,
    filtro_area: Optional[str] = None,
    filtro_prioridad: Optional[str] = None,
    busqueda: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Recupera los informes institucionales almacenados con filtros y buscador de texto.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        query = "SELECT * FROM Informes_Sanitarios WHERE 1=1"
        params = []
        
        if filtro_tipo and filtro_tipo != "Todos":
            query += " AND tipo_informe = ?"
            params.append(filtro_tipo)
            
        if filtro_area and filtro_area != "Todas":
            query += " AND area_servicio = ?"
            params.append(filtro_area)
            
        if filtro_prioridad and filtro_prioridad != "Todas":
            query += " AND prioridad = ?"
            params.append(filtro_prioridad)
            
        if busqueda and busqueda.strip():
            query += " AND (titulo LIKE ? OR contenido LIKE ? OR resumen LIKE ? OR autor LIKE ?)"
            term = f"%{busqueda.strip()}%"
            params.extend([term, term, term, term])
            
        query += " ORDER BY fecha_informe DESC, id DESC;"
        
        cursor.execute(query, params)
        filas = cursor.fetchall()
        resultados = []
        for f in filas:
            item = dict(f)
            try:
                item["rutas_imagenes"] = json.loads(item["rutas_imagenes"]) if item["rutas_imagenes"] else []
            except Exception:
                item["rutas_imagenes"] = []
            resultados.append(item)
        return resultados


def obtener_informe_por_id(informe_id: int) -> Optional[Dict[str, Any]]:
    """Recupera un informe específico por su ID."""
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM Informes_Sanitarios WHERE id = ?;", (informe_id,))
        fila = cursor.fetchone()
        if not fila:
            return None
        item = dict(fila)
        try:
            item["rutas_imagenes"] = json.loads(item["rutas_imagenes"]) if item["rutas_imagenes"] else []
        except Exception:
            item["rutas_imagenes"] = []
        return item


def eliminar_informe(informe_id: int) -> bool:
    """Elimina un informe institucional de la base de datos."""
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM Informes_Sanitarios WHERE id = ?;", (informe_id,))
        conexion.commit()
        return cursor.rowcount > 0


def obtener_metricas_informes() -> Dict[str, Any]:
    """Calcula métricas sintéticas sobre los informes registrados."""
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM Informes_Sanitarios;")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS criticos FROM Informes_Sanitarios WHERE prioridad IN ('Crítica/Inmediata', 'Alta');")
        criticos = cursor.fetchone()["criticos"]

        cursor.execute("SELECT COUNT(*) AS con_imagenes FROM Informes_Sanitarios WHERE rutas_imagenes IS NOT NULL AND rutas_imagenes != '[]';")
        con_imagenes = cursor.fetchone()["con_imagenes"]

        cursor.execute("SELECT tipo_informe, COUNT(*) as cantidad FROM Informes_Sanitarios GROUP BY tipo_informe;")
        tipos = {r["tipo_informe"]: r["cantidad"] for r in cursor.fetchall()}

        cursor.execute("SELECT area_servicio, COUNT(*) as cantidad FROM Informes_Sanitarios GROUP BY area_servicio;")
        areas = {r["area_servicio"]: r["cantidad"] for r in cursor.fetchall()}

        return {
            "total": total,
            "criticos": criticos,
            "con_imagenes": con_imagenes,
            "tipos": tipos,
            "areas": areas
        }


def poblar_informes_ejemplo():
    """Genera informes técnicos y sanitarios iniciales para el CAPS Dr. Luis Gianotti."""
    informes_demo = [
        {
            "titulo": "Relevamiento de Mantenimiento y Calibración de Autoclave de Esterilización",
            "fecha_informe": date.today().strftime("%Y-%m-%d"),
            "tipo_informe": "Técnico / Mantenimiento Electromédico",
            "area_servicio": "Bioingeniería y Tecnología Médica",
            "autor": "Área de Bioingeniería - FI UNER",
            "prioridad": "Alta",
            "estado": "Aprobado",
            "resumen": "Inspección técnica de sellos de presión, sensores de temperatura y ciclos de vacío del autoclave del área de odontología y enfermería.",
            "contenido": "Se realizó la verificación trimestral del autoclave a vapor de mesa (18 Lts) utilizado para la esterilización de instrumental odontológico y quirúrgico menor. Se detectó una ligera fuga de vapor en la junta de silicona de la compuerta principal que provoca demoras en alcanzar los 134°C requeridos. Los indicadores biológicos dieron conformes, pero se recomienda el recambio preventivo del empaque antes de que impacte en la disponibilidad del instrumental.",
            "recomendaciones": "1. Reemplazo inmediato de la junta tórica de sellado.\n2. Recalibración del transductor de presión manométrica.\n3. Registro en planilla de verificación de bioseguridad del efector.",
            "rutas_imagenes": []
        },
        {
            "titulo": "Auditoría de Cadena de Frío y Monitoreo Térmico en Vacunatorio",
            "fecha_informe": date.today().strftime("%Y-%m-%d"),
            "tipo_informe": "Auditoría y Gestión Institucional",
            "area_servicio": "Enfermería y Vacunatorio",
            "autor": "Lic. en Enfermería / Coordinación CAPS",
            "prioridad": "Crítica/Inmediata",
            "estado": "En Seguimiento",
            "resumen": "Control de data loggers y termómetros de máxima-mínima en heladeras de biológicos tras microcortes de energía en Oro Verde.",
            "contenido": "Tras las tormentas eléctricas del último fin de semana y microcortes registrados en la red eléctrica comunitaria de Oro Verde, se auditó el registro continuo de temperatura de las dos heladeras de conservación de biológicos del Programa Ampliado de Inmunizaciones (PAI). La heladera N°1 mantuvo el rango normativo (2°C a 8°C) gracias al sistema de contingencia de paquetes fríos, mientras que la heladera N°2 registró un pico transitorio de 9.1°C durante 25 minutos. Se confirmó la viabilidad de las vacunas según tabla de estabilidad del Ministerio de Salud.",
            "recomendaciones": "1. Evaluar instalación de UPS de grado médico de 2 kVA para sostener el banco de frío.\n2. Incorporar alerta remota por telemetría IoT vinculada al celular de guardia.",
            "rutas_imagenes": []
        },
        {
            "titulo": "Informe Epidemiológico: Vigilancia de Infecciones Respiratorias Agudas Bajas (IRAB)",
            "fecha_informe": date.today().strftime("%Y-%m-%d"),
            "tipo_informe": "Epidemiológico y Vigilancia Sanitaria",
            "area_servicio": "Pediatría",
            "autor": "Dra. Médica Pediatra de Guardia",
            "prioridad": "Media",
            "estado": "Aprobado",
            "resumen": "Incremento de consultas de bronquiolitis y broncoespasmos en niños menores de 5 años procedentes de los barrios El Triangular y 50 Viviendas.",
            "contenido": "Durante el último mes epidemiológico se registró un incremento del 38% en las consultas de demanda espontánea por patología respiratoria obstructiva en pacientes lactantes y pediátricos. La mayoría de los casos proviene de zonas de mayor exposición a factores ambientales como calles de ripio con polvo en suspensión o calefacción precaria. Se articuló con el hospital de referencia San Roque en Paraná para la derivación oportuna de los 3 casos que requirieron oxigenoterapia de alto flujo.",
            "recomendaciones": "1. Aumentar el stock asignado de aerosoles de Salbutamol y aerocámaras infantiles.\n2. Desarrollar talleres de pautas de alarma respiratoria en salas de espera para familias.",
            "rutas_imagenes": []
        }
    ]
    for inf in informes_demo:
        registrar_informe_sanitario(**inf)


# =====================================================================
# PLATAFORMA RELEVAR: GESTIÓN DE RELEVAMIENTOS PONDERADOS Y TALLERES
# Conforme a: "Plataforma de trazabilidad de indicadores de la salud y
# gestión de talleres comunitarios mediante el relevamiento de datos ponderados"
# FIUNER - CiC Luis Gianotti - Oro Verde
# =====================================================================

def registrar_relevamiento_relevar(
    tipo_poblacion: str,
    rango_etario: Optional[str],
    genero: Optional[str],
    barrio_o_residencia: Optional[str],
    carrera: Optional[str],
    ano_cursado: Optional[str],
    situacion_habitacional: Optional[str],
    factores_vulnerabilidad: List[str],
    factores_protectores: List[str],
    puntaje_vulnerabilidad: float,
    puntaje_proteccion: float,
    indice_riesgo_ponderado: float,
    nivel_prioridad: str,
    observaciones_libres: Optional[str] = None,
    canal: str = "Formulario RELEVAR Web"
) -> int:
    """
    Registra un formulario anónimo de la Planilla de Agentes Sanitarios (RELEVAR)
    con sus cálculos ponderados de vulnerabilidad, protección y riesgo.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Relevamiento_Relevar (
                fecha_hora, tipo_poblacion, rango_etario, genero, barrio_o_residencia,
                carrera, ano_cursado, situacion_habitacional, factores_vulnerabilidad,
                factores_protectores, puntaje_vulnerabilidad, puntaje_proteccion,
                indice_riesgo_ponderado, nivel_prioridad, observaciones_libres, canal
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            );
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            tipo_poblacion,
            rango_etario,
            genero,
            barrio_o_residencia,
            carrera,
            ano_cursado,
            situacion_habitacional,
            json.dumps(factores_vulnerabilidad, ensure_ascii=False),
            json.dumps(factores_protectores, ensure_ascii=False),
            round(puntaje_vulnerabilidad, 2),
            round(puntaje_proteccion, 2),
            round(indice_riesgo_ponderado, 2),
            nivel_prioridad,
            observaciones_libres.strip() if observaciones_libres else None,
            canal
        ))
        conexion.commit()
        return cursor.lastrowid


def obtener_relevamientos_relevar(
    filtro_poblacion: Optional[str] = None,
    filtro_prioridad: Optional[str] = None,
    filtro_carrera: Optional[str] = None,
    filtro_barrio: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Recupera los relevamientos sanitarios con filtros para el tablero de trazabilidad.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        query = "SELECT * FROM Relevamiento_Relevar WHERE 1=1"
        params = []

        if filtro_poblacion and filtro_poblacion != "Todas":
            query += " AND tipo_poblacion = ?"
            params.append(filtro_poblacion)

        if filtro_prioridad and filtro_prioridad != "Todas":
            query += " AND nivel_prioridad = ?"
            params.append(filtro_prioridad)

        if filtro_carrera and filtro_carrera != "Todas":
            query += " AND carrera = ?"
            params.append(filtro_carrera)

        if filtro_barrio and filtro_barrio != "Todos":
            query += " AND barrio_o_residencia = ?"
            params.append(filtro_barrio)

        query += " ORDER BY fecha_hora DESC, id DESC;"
        cursor.execute(query, params)
        filas = cursor.fetchall()
        
        resultados = []
        for f in filas:
            item = dict(f)
            try:
                item["factores_vulnerabilidad"] = json.loads(item["factores_vulnerabilidad"])
            except Exception:
                item["factores_vulnerabilidad"] = []
            try:
                item["factores_protectores"] = json.loads(item["factores_protectores"])
            except Exception:
                item["factores_protectores"] = []
            resultados.append(item)
        return resultados


def obtener_metricas_relevar() -> Dict[str, Any]:
    """
    Calcula agregaciones epidemiológicas de los relevamientos RELEVAR:
    Índices promedio de vulnerabilidad, protección, balance de salud mental y distribución poblacional.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        
        cursor.execute("SELECT COUNT(*) AS total FROM Relevamiento_Relevar;")
        total = cursor.fetchone()["total"]

        if total == 0:
            return {
                "total": 0,
                "fiuner_total": 0,
                "comunidad_total": 0,
                "ivp_promedio": 0.0,
                "ifp_promedio": 0.0,
                "riesgo_promedio": 0.0,
                "prioridades": {},
                "factores_vuln_conteo": {},
                "factores_prot_conteo": {},
                "salud_mental_prevalencia": 0.0
            }

        cursor.execute("SELECT COUNT(*) AS total FROM Relevamiento_Relevar WHERE tipo_poblacion LIKE '%FIUNER%' OR tipo_poblacion LIKE '%Estudiante%';")
        fiuner_total = cursor.fetchone()["total"]

        comunidad_total = total - fiuner_total

        cursor.execute("SELECT AVG(puntaje_vulnerabilidad) AS ivp, AVG(puntaje_proteccion) AS ifp, AVG(indice_riesgo_ponderado) AS riesgo FROM Relevamiento_Relevar;")
        row_avg = cursor.fetchone()
        ivp_promedio = round(row_avg["ivp"] or 0.0, 1)
        ifp_promedio = round(row_avg["ifp"] or 0.0, 1)
        riesgo_promedio = round(row_avg["riesgo"] or 0.0, 1)

        cursor.execute("SELECT nivel_prioridad, COUNT(*) as cantidad FROM Relevamiento_Relevar GROUP BY nivel_prioridad;")
        prioridades = {r["nivel_prioridad"]: r["cantidad"] for r in cursor.fetchall()}

        # Frecuencia de factores
        cursor.execute("SELECT factores_vulnerabilidad, factores_protectores FROM Relevamiento_Relevar;")
        all_filas = cursor.fetchall()
        
        vuln_conteo: Dict[str, int] = {}
        prot_conteo: Dict[str, int] = {}
        salud_mental_count = 0

        claves_salud_mental = [
            "Estrés académico o laboral severo / agotamiento cognitivo",
            "Episodios frecuentes de ansiedad o angustia",
            "Trastornos del sueño o insomnio crónico",
            "Aislamiento social / desarraigo familiar",
            "Problema de salud mental diagnosticado sin apoyo"
        ]

        for fila in all_filas:
            try:
                v_list = json.loads(fila["factores_vulnerabilidad"])
            except Exception:
                v_list = []
            try:
                p_list = json.loads(fila["factores_protectores"])
            except Exception:
                p_list = []

            tiene_sm = False
            for v in v_list:
                vuln_conteo[v] = vuln_conteo.get(v, 0) + 1
                if any(sm in v for sm in ["Estrés", "ansiedad", "sueño", "Aislamiento", "salud mental"]):
                    tiene_sm = True

            if tiene_sm:
                salud_mental_count += 1

            for p in p_list:
                prot_conteo[p] = prot_conteo.get(p, 0) + 1

        sm_prevalencia = round((salud_mental_count / total * 100), 1) if total > 0 else 0.0

        return {
            "total": total,
            "fiuner_total": fiuner_total,
            "comunidad_total": comunidad_total,
            "ivp_promedio": ivp_promedio,
            "ifp_promedio": ifp_promedio,
            "riesgo_promedio": riesgo_promedio,
            "prioridades": prioridades,
            "factores_vuln_conteo": vuln_conteo,
            "factores_prot_conteo": prot_conteo,
            "salud_mental_prevalencia": sm_prevalencia
        }


def obtener_todos_los_talleres(
    estado_filtro: Optional[str] = "Activo",
    categoria_filtro: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Recupera los talleres comunitarios de la base de datos persistente.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        query = "SELECT * FROM Talleres_Sistema WHERE 1=1"
        params = []

        if estado_filtro and estado_filtro != "Todos":
            query += " AND estado = ?"
            params.append(estado_filtro)

        if categoria_filtro and categoria_filtro != "Todas":
            query += " AND categoria = ?"
            params.append(categoria_filtro)

        query += " ORDER BY destacado_carrusel DESC, titulo ASC;"
        cursor.execute(query, params)
        filas = cursor.fetchall()
        
        talleres = []
        for f in filas:
            item = dict(f)
            try:
                item["responde_a"] = json.loads(item["responde_a"])
            except Exception:
                item["responde_a"] = []
            talleres.append(item)
        return talleres


def registrar_nuevo_taller(
    id_taller: str,
    titulo: str,
    categoria: str,
    icono: str,
    descripcion: str,
    detalle_ampliado: str,
    responde_a: List[str],
    publico_objetivo: str,
    lugar: str,
    horario: str,
    frecuencia: str,
    coordinacion: str,
    requisitos: str,
    estado: str = "Activo",
    es_ficticio: int = 0,
    destacado_carrusel: int = 0,
    imagen_url: Optional[str] = None
) -> bool:
    """
    Inserta un nuevo taller o propuesta de abordaje en la base de datos.
    """
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO Talleres_Sistema (
                id, titulo, categoria, icono, descripcion, detalle_ampliado,
                responde_a, publico_objetivo, lugar, horario, frecuencia,
                coordinacion, requisitos, estado, es_ficticio, destacado_carrusel,
                imagen_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            id_taller,
            titulo.strip(),
            categoria.strip(),
            icono.strip(),
            descripcion.strip(),
            detalle_ampliado.strip(),
            json.dumps(responde_a, ensure_ascii=False),
            publico_objetivo,
            lugar.strip(),
            horario.strip(),
            frecuencia.strip(),
            coordinacion.strip(),
            requisitos.strip(),
            estado,
            es_ficticio,
            destacado_carrusel,
            imagen_url
        ))
        conexion.commit()
        return True


def cambiar_estado_taller(id_taller: str, nuevo_estado: str) -> bool:
    """Cambia el estado de un taller (ej. de 'Sugerido' a 'Activo' o 'En Pausa')."""
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("UPDATE Talleres_Sistema SET estado = ? WHERE id = ?;", (nuevo_estado, id_taller))
        conexion.commit()
        return cursor.rowcount > 0


def incrementar_interes_taller(id_taller: str) -> int:
    """Incrementa el contador de interesados/inscritos comunitarios en un taller."""
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("UPDATE Talleres_Sistema SET interesados_contador = interesados_contador + 1 WHERE id = ?;", (id_taller,))
        cursor.execute("SELECT interesados_contador FROM Talleres_Sistema WHERE id = ?;", (id_taller,))
        row = cursor.fetchone()
        conexion.commit()
        return row["interesados_contador"] if row else 1


def inicializar_talleres_predeterminados():
    """Puebla los talleres iniciales oficiales y de la prueba piloto FIUNER en la tabla."""
    with obtener_conexion() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM Talleres_Sistema;")
        if cursor.fetchone()["total"] > 0:
            return

    talleres_base = [
        # TALLERES ORIENTADOS A ESTUDIANTES Y SALUD MENTAL UNIVERSITARIA (FIUNER)
        {
            "id_taller": "taller-fiuner-01",
            "titulo": "Manejo del Estrés Académico, Ansiedad y Concentración",
            "categoria": "Salud mental y bienestar",
            "icono": "🧠",
            "descripcion": "Estrategias de regulación emocional, técnicas de respiración y planificación cognitiva para afrontar parciales y entregas.",
            "detalle_ampliado": (
                "Dispositivo grupal coordinado por profesionales de la salud mental del CIC Gianotti y el equipo pedagógico de FIUNER. "
                "Se abordan técnicas de desactivación fisiológica (respiración diafragmática, relajación muscular progresiva de Jacobson), "
                "reestructuración de pensamientos catastrofistas ante exámenes, herramientas para superar la procrastinación por sobrecarga, "
                "y fortalecimiento de redes de apoyo entre compañeros para evitar la soledad en la vida universitaria."
            ),
            "responde_a": [
                "Estrés académico o laboral severo / agotamiento cognitivo",
                "Episodios frecuentes de ansiedad o angustia",
                "Aislamiento social / desarraigo familiar"
            ],
            "publico_objetivo": "Estudiantes Universitarios (FIUNER)",
            "lugar": "FIUNER (Aula Magna / Espacio de Salud)",
            "horario": "Jueves · 17:30 h",
            "frecuencia": "Semanal (Duración: 1h 30m)",
            "coordinacion": "Lic. en Psicología (CIC Gianotti) y Tutoría Estudiantil FIUNER",
            "requisitos": "Abierto y gratuito para estudiantes de Bioingeniería, Bioinformática y Tecnicaturas. No se requiere inscripción previa.",
            "estado": "Activo",
            "es_ficticio": 0,
            "destacado_carrusel": 1,
            "imagen_url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id_taller": "taller-fiuner-02",
            "titulo": "Higiene del Sueño y Ritmos Circadianos en Universitarios",
            "categoria": "Salud mental y bienestar",
            "icono": "💤",
            "descripcion": "Cómo reparar el descanso nocturno, evitar la sobreexposición a pantallas y mejorar el rendimiento cognitivo sin automedicación.",
            "detalle_ampliado": (
                "Taller interdisciplinario entre medicina del sueño y bioingeniería para abordar el insomnio habitual en los períodos de exámenes. "
                "Se explican los ciclos de sueño REM y no-REM, el impacto de la luz azul en la melatonina, cómo programar siestas estratégicas ("
                "power naps) y alternativas saludables para evitar el abuso de cafeína, bebidas energizantes o psicofármacos sin receta."
            ),
            "responde_a": [
                "Trastornos del sueño o insomnio crónico",
                "Estrés académico o laboral severo / agotamiento cognitivo"
            ],
            "publico_objetivo": "Estudiantes Universitarios (FIUNER)",
            "lugar": "CiC 'Gianotti' / FIUNER Auditorio",
            "horario": "Martes · 18:00 h",
            "frecuencia": "Quincenal",
            "coordinacion": "Médico Clínico (CIC) y Docentes de Neurofisiología (FIUNER)",
            "requisitos": "Gratuito. Podés llevar cuaderno de notas.",
            "estado": "Activo",
            "es_ficticio": 0,
            "destacado_carrusel": 1,
            "imagen_url": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id_taller": "taller-fiuner-03",
            "titulo": "Pausas Activas, Ergonomía y Prevención del Dolor Postural",
            "categoria": "Prevención y cuidados",
            "icono": "🧘",
            "descripcion": "Ejercicios para cuello, columna y muñecas tras largas horas frente a la computadora o apuntes.",
            "detalle_ampliado": (
                "Práctica orientada por el servicio de Kinesiología del CIC Gianotti y especialistas en ergonomía biomédica de la facultad. "
                "Enseña cómo regular la altura de pantallas y sillas de estudio caseras, posturas correctas, estiramientos de cadenas musculares "
                "acortadas (isquiotibiales, trapecios, flexores de muñeca para prevenir túnel carpiano) y ejercicios de respiración activa."
            ),
            "responde_a": [
                "Dolores osteomusculares o cefaleas frecuentes",
                "Sedentarismo o inactividad física severa"
            ],
            "publico_objetivo": "Comunidad Universitaria y Residentes",
            "lugar": "Playón Deportivo FIUNER / CiC Gianotti",
            "horario": "Miércoles · 12:30 h (Mediodía)",
            "frecuencia": "Semanal",
            "coordinacion": "Lic. en Kinesiología y Fisiatría (CIC Gianotti)",
            "requisitos": "Ropa cómoda. No se precisa colchoneta.",
            "estado": "Activo",
            "es_ficticio": 0,
            "destacado_carrusel": 0,
            "imagen_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id_taller": "taller-fiuner-04",
            "titulo": "Cocina Práctica, Nutrición y Ahorro para Estudiantes",
            "categoria": "Salud Comunitaria y Nutrición",
            "icono": "🥗",
            "descripcion": "Recetas económicas de alto valor nutritivo, planificación semanal (Meal Prep) y prevención de la anemia.",
            "detalle_ampliado": (
                "Espacio dinámico orientado a estudiantes que viven solos o comparten alquiler en Oro Verde. "
                "Estrategias para comprar en ferias locales, cocinar en tandas para la semana, garantizar el consumo de hierro, proteínas y legumbres "
                "con bajo presupuesto, y evitar el salteo habitual del desayuno o almuerzo por horarios de cursada."
            ),
            "responde_a": [
                "Mala nutrición o salteo recurrente de comidas",
                "Inestabilidad económica severa / dificultad de sustento"
            ],
            "publico_objetivo": "Estudiantes y Jóvenes de Oro Verde",
            "lugar": "CiC 'Gianotti' - Cocina Comunitaria",
            "horario": "Sábados · 11:00 h",
            "frecuencia": "Quincenal",
            "coordinacion": "Lic. en Nutrición (CIC Gianotti)",
            "requisitos": "Gratuito. Se degustan las recetas preparadas.",
            "estado": "Activo",
            "es_ficticio": 1,
            "destacado_carrusel": 1,
            "imagen_url": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80"
        },
        # TALLERES COMUNITARIOS CLÁSICOS DEL CIC LUIS GIANOTTI
        {
            "id_taller": "taller-cic-01",
            "titulo": "Embarazo Joven y Maternidad Acompañada",
            "categoria": "Materno-infantil",
            "icono": "🤰",
            "descripcion": "Controles obstétricos, derechos del paciente y red comunitaria de apoyo para jóvenes gestantes.",
            "detalle_ampliado": (
                "Espacio integral de preparación para la maternidad y paternidad, controles del embarazo en el CAPS, "
                "pautas de nutrición, derechos en el parto respetado y articulación con asignaciones sociales."
            ),
            "responde_a": [
                "Embarazo o maternidad/paternidad en edad temprana",
                "Vivienda precaria / hacinamiento en el hogar"
            ],
            "publico_objetivo": "Comunidad de Oro Verde",
            "lugar": "CiC 'Gianotti'",
            "horario": "Miércoles · 15:00 h",
            "frecuencia": "Semanal",
            "coordinacion": "Lic. Obstétrica y Lic. en Trabajo Social",
            "requisitos": "Abierto y 100% gratuito. Podés concurrir acompañada.",
            "estado": "Activo",
            "es_ficticio": 0,
            "destacado_carrusel": 0,
            "imagen_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id_taller": "taller-cic-02",
            "titulo": "Vacunas y Controles de Niño Sano",
            "categoria": "Prevención y cuidados",
            "icono": "👶",
            "descripcion": "Revisión del carnet de vacunación, seguimiento del percentilo de crecimiento y salud infantil.",
            "detalle_ampliado": (
                "Control periódico de salud infantil, peso, talla, desarrollo psicomotor y aplicación de vacunas obligatorias "
                "del Calendario Nacional sin turno y por orden de llegada."
            ),
            "responde_a": [
                "Esquema de vacunación incompleto o desactualizado",
                "Persona a cargo de cuidados familiares intensivos"
            ],
            "publico_objetivo": "Familias con niños pequeños",
            "lugar": "CiC 'Gianotti' - Vacunatorio",
            "horario": "Martes · 9:00 h",
            "frecuencia": "Semanal",
            "coordinacion": "Equipo de Enfermería y Pediatra",
            "requisitos": "Traer DNI y libreta sanitaria o carnet de vacunas.",
            "estado": "Activo",
            "es_ficticio": 0,
            "destacado_carrusel": 0,
            "imagen_url": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id_taller": "taller-cic-03",
            "titulo": "Espacio de Escucha y Deshabituación de Consumos",
            "categoria": "Salud mental y bienestar",
            "icono": "🚭",
            "descripcion": "Encuentros confidenciales y no punitivos sobre alcohol, sustancias y cesación tabáquica.",
            "detalle_ampliado": (
                "Dispositivo grupal de umbral bajo, con abordaje de reducción de daños para consumos problemáticos "
                "y acompañamiento médico para dejar el cigarrillo."
            ),
            "responde_a": [
                "Consumo problemático de sustancias (alcohol, tabaco o psicofármacos)",
                "Episodios frecuentes de ansiedad o angustia"
            ],
            "publico_objetivo": "Jóvenes y Adultos de Oro Verde",
            "lugar": "CiC 'Gianotti' - Sala Interdisciplinaria",
            "horario": "Lunes · 18:30 h",
            "frecuencia": "Semanal",
            "coordinacion": "Lic. en Psicología y Operadores Sociocomunitarios",
            "requisitos": "Confidencial y libre. No se juzga ni se exigen antecedentes.",
            "estado": "Activo",
            "es_ficticio": 0,
            "destacado_carrusel": 0,
            "imagen_url": "https://images.unsplash.com/photo-1527137342181-19aab11a8ee8?auto=format&fit=crop&w=800&q=80"
        },
        {
            "id_taller": "taller-cic-04",
            "titulo": "Envejecimiento Activo, Prevención de Caídas y Memoria",
            "categoria": "Tercera edad y autonomía",
            "icono": "🧓",
            "descripcion": "Ejercicios de equilibrio, estimulación neurocognitiva y controles de presión arterial en adultos mayores.",
            "detalle_ampliado": (
                "Taller de promoción para personas mayores de Oro Verde. Incluye estimulación de memoria, juegos de agilidad mental, "
                "movilidad articular para prevenir fracturas y contención comunitaria contra la soledad no deseada."
            ),
            "responde_a": [
                "Enfermedad crónica sin control regular",
                "Aislamiento social / desarraigo familiar",
                "Persona a cargo de cuidados familiares intensivos"
            ],
            "publico_objetivo": "Adultos Mayores y Cuidadores",
            "lugar": "CiC 'Gianotti' - Salón Comunitario",
            "horario": "Viernes · 10:00 h",
            "frecuencia": "Semanal",
            "coordinacion": "Kinesióloga, Médica Generalista y Talleristas",
            "requisitos": "Gratuito. Abierto a jubilados y pensionados.",
            "estado": "Activo",
            "es_ficticio": 0,
            "destacado_carrusel": 0,
            "imagen_url": "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?auto=format&fit=crop&w=800&q=80"
        }
    ]

    for t in talleres_base:
        registrar_nuevo_taller(**t)


def poblar_datos_relevar_demo():
    """
    Puebla relevamientos de demostración para la prueba piloto FIUNER
    y la comunidad de Oro Verde, reflejando la realidad epidemiológica descripta en el PDF.
    """
    casos_demo = [
        # CASOS ESTUDIANTILES FIUNER (Prueba Piloto: Carga cognitiva, estrés normalizado, desarraigo)
        {
            "tipo_poblacion": "Estudiante FIUNER (Prueba Piloto)",
            "rango_etario": "18 - 24 años",
            "genero": "Femenino",
            "barrio_o_residencia": "Estudiante",
            "carrera": "Bioingeniería",
            "ano_cursado": "3er año",
            "situacion_habitacional": "Alquila con compañeros de estudio",
            "factores_vulnerabilidad": [
                "Estrés académico o laboral severo / agotamiento cognitivo",
                "Episodios frecuentes de ansiedad o angustia",
                "Trastornos del sueño o insomnio crónico",
                "Dolores osteomusculares o cefaleas frecuentes"
            ],
            "factores_protectores": [
                "Cuenta con red sólida de amigos o compañeros",
                "Tiene cobertura médica o sabe cómo atenderse en el CIC",
                "Siente que puede pedir ayuda ante un malestar"
            ],
            "puntaje_vulnerabilidad": 58.2,
            "puntaje_proteccion": 45.0,
            "indice_riesgo_ponderado": 35.7,
            "nivel_prioridad": "Moderado",
            "observaciones_libres": "Cursando materias de alta carga matemática. Época de parciales con dolores de cabeza continuos y noches de 4 horas de sueño."
        },
        {
            "tipo_poblacion": "Estudiante FIUNER (Prueba Piloto)",
            "rango_etario": "18 - 24 años",
            "genero": "Masculino",
            "barrio_o_residencia": "Estudiante",
            "carrera": "Bioingeniería",
            "ano_cursado": "2do año",
            "situacion_habitacional": "Alquila solo (oriundo del interior de Entre Ríos)",
            "factores_vulnerabilidad": [
                "Estrés académico o laboral severo / agotamiento cognitivo",
                "Trastornos del sueño o insomnio crónico",
                "Aislamiento social / desarraigo familiar",
                "Mala nutrición o salteo recurrente de comidas",
                "Inestabilidad económica severa / dificultad de sustento"
            ],
            "factores_protectores": [
                "Realiza actividad física o deporte regular (2+ veces/semana)",
                "Dispone de un entorno tranquilo para estudiar"
            ],
            "puntaje_vulnerabilidad": 72.5,
            "puntaje_proteccion": 24.0,
            "indice_riesgo_ponderado": 60.5,
            "nivel_prioridad": "Alto",
            "observaciones_libres": "Vivir solo lejos de la familia complica la organización de las comidas. El desarraigo se siente mucho los fines de semana."
        },
        {
            "tipo_poblacion": "Estudiante FIUNER (Prueba Piloto)",
            "rango_etario": "25 - 30 años",
            "genero": "Masculino",
            "barrio_o_residencia": "Otro/Foráneo",
            "carrera": "Lic. en Bioinformática",
            "ano_cursado": "4to año",
            "situacion_habitacional": "Vive con familia de origen",
            "factores_vulnerabilidad": [
                "Estrés académico o laboral severo / agotamiento cognitivo",
                "Dolores osteomusculares o cefaleas frecuentes"
            ],
            "factores_protectores": [
                "Cuenta con red sólida de amigos o compañeros",
                "Realiza actividad física o deporte regular (2+ veces/semana)",
                "Tiene cobertura médica o sabe cómo atenderse en el CIC",
                "Mantiene rutinas ordenadas de descanso y alimentación",
                "Dedica tiempo semanal a hobbies y esparcimiento"
            ],
            "puntaje_vulnerabilidad": 24.5,
            "puntaje_proteccion": 68.0,
            "indice_riesgo_ponderado": 0.0,
            "nivel_prioridad": "Bajo",
            "observaciones_libres": "Buena contención en casa, aunque viajar en colectivo todos los días suma cansancio."
        },
        {
            "tipo_poblacion": "Estudiante FIUNER (Prueba Piloto)",
            "rango_etario": "18 - 24 años",
            "genero": "Femenino",
            "barrio_o_residencia": "Estudiante",
            "carrera": "Bioingeniería",
            "ano_cursado": "1er año",
            "situacion_habitacional": "Alquila en residencia compartida",
            "factores_vulnerabilidad": [
                "Estrés académico o laboral severo / agotamiento cognitivo",
                "Episodios frecuentes de ansiedad o angustia",
                "Trastornos del sueño o insomnio crónico",
                "Aislamiento social / desarraigo familiar",
                "Problema de salud mental diagnosticado sin apoyo"
            ],
            "factores_protectores": [
                "Dispone de un entorno tranquilo para estudiar"
            ],
            "puntaje_vulnerabilidad": 82.0,
            "puntaje_proteccion": 12.0,
            "indice_riesgo_ponderado": 76.0,
            "nivel_prioridad": "Crítico",
            "observaciones_libres": "Crisis de pánico antes de rendir y dificultades para adaptarme a la ciudad."
        },
        # CASOS COMUNIDAD DE ORO VERDE (Extensión y APS)
        {
            "tipo_poblacion": "Comunidad General (Oro Verde / CIC)",
            "rango_etario": "31 - 45 años",
            "genero": "Femenino",
            "barrio_o_residencia": "Residente de Oro Verde",
            "carrera": None,
            "ano_cursado": None,
            "situacion_habitacional": "Vivienda propia familiar",
            "factores_vulnerabilidad": [
                "Inestabilidad económica severa / dificultad de sustento",
                "Persona a cargo de cuidados familiares intensivos",
                "Enfermedad crónica sin control regular"
            ],
            "factores_protectores": [
                "Cuenta con red sólida de amigos o compañeros",
                "Tiene cobertura médica o sabe cómo atenderse en el CIC",
                "Participa en actividades o talleres comunitarios"
            ],
            "puntaje_vulnerabilidad": 46.0,
            "puntaje_proteccion": 45.0,
            "indice_riesgo_ponderado": 23.5,
            "nivel_prioridad": "Bajo",
            "observaciones_libres": "Madre de 3 chicos, concurre regularmente a la enfermería del CIC."
        },
        {
            "tipo_poblacion": "Comunidad General (Oro Verde / CIC)",
            "rango_etario": "60+ años",
            "genero": "Femenino",
            "barrio_o_residencia": "Residente de Oro Verde",
            "carrera": None,
            "ano_cursado": None,
            "situacion_habitacional": "Vive sola",
            "factores_vulnerabilidad": [
                "Enfermedad crónica sin control regular",
                "Aislamiento social / desarraigo familiar"
            ],
            "factores_protectores": [
                "Tiene cobertura médica o sabe cómo atenderse en el CIC",
                "Dedica tiempo semanal a hobbies y esparcimiento"
            ],
            "puntaje_vulnerabilidad": 32.0,
            "puntaje_proteccion": 30.0,
            "indice_riesgo_ponderado": 17.0,
            "nivel_prioridad": "Bajo",
            "observaciones_libres": "Control de presión arterial en el Gianotti."
        }
    ]

    for c in casos_demo:
        registrar_relevamiento_relevar(**c)


