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

