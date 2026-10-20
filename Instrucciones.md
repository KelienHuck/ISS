# Sistema de Relevamiento Comunitario e Interacción Ciudadana
## Centro de Atención Primaria de la Salud (CAPS) "Dr. Luis Gianotti" - Oro Verde, Entre Ríos
**Cátedra:** Introducción a los Sistemas de Salud  
**Carrera:** Bioingeniería - Facultad de Ingeniería (UNER)  

---

## 🏛️ Contexto y Misión Sanitaria
Este Producto Mínimo Viable (MVP) responde a la necesidad de fortalecer la **Atención Primaria de la Salud (APS)** orientada a la comunidad de Oro Verde. En lugar de limitarse a registros administrativos cerrados, la plataforma empodera a los vecinos y vecinas para manifestar sus vivencias, necesidades y quejas en lenguaje natural.

Mediante un **asistente de triaje social potenciado por un modelo de lenguaje local (Ollama)**, los relatos ciudadanos no estructurados se transforman en variables epidemiológicas cuantitativas (categoría de reclamo, urgencia sanitaria y sentimiento social), preservando la privacidad bajo la **Ley Nacional 25.326 de Protección de los Datos Personales de la República Argentina**.

---

## 🛠️ Estructura Arquitectónica del Proyecto
```
c:\Users\LENOVO\Desktop\Facultad\Salud\
├── database.py         # Persistencia SQLite (Relevamientos comunitarios e índices)
├── ai_triage.py        # Módulo de triaje de lenguaje natural y conexión con Ollama
├── app.py              # Plataforma interactiva Streamlit (Talleres, Portal y Tablero)
├── requirements.txt    # Dependencias del proyecto
├── uploads/            # Almacenamiento seguro de evidencias fotográficas adjuntas
│   └── ciudadanos/     # Fotografías voluntarias adjuntadas en reclamos
└── README.md           # Documentación técnica, académica y guía de despliegue
```

---

## 🚀 Guía de Instalación y Ejecución Paso a Paso

### 1. Requisitos Previos
* **Python 3.10 o superior** instalado en el sistema.
* **Ollama** descargado e instalado desde [https://ollama.com](https://ollama.com).

### 2. Configuración y Descarga del Modelo en Ollama
Abre una terminal (PowerShell o CMD) y descarga el modelo de lenguaje sugerido:
```powershell
# Descarga del modelo de lenguaje (Llama 3 8B o Llama 3.2 3B para equipos con menos RAM)
ollama pull llama3:8b

# Si tu computadora cuenta con recursos limitados (menos de 8GB de RAM o sin GPU dedicada):
ollama pull llama3.2:3b
```
Para asegurarte de que el servicio está activo en segundo plano:
```powershell
ollama serve
```

### 3. Instalación de Dependencias de Python
En la carpeta del proyecto (`c:\Users\LENOVO\Desktop\Facultad\Salud`):
```powershell
# Creación de entorno virtual (recomendado)
python -m venv venv
.\venv\Scripts\activate

# Instalación de paquetes
pip install -r requirements.txt
```

### 4. Ejecución de la Aplicación Web
Inicia la plataforma web local con Streamlit:
```powershell
streamlit run app.py
```
La aplicación se abrirá automáticamente en tu navegador web en `http://localhost:8501`.

---

## 🌐 ¿Si hosteo la página, las personas pueden verla?

**Sí, absolutamente.** Al hostear la aplicación web en un servidor o plataforma en la nube, se genera un enlace público seguro (URL con `https://`) que cualquier persona puede abrir desde su celular, tablet o computadora conectada a internet.

### Opciones sencillas para hostearla:

1. **Streamlit Community Cloud (Recomendada y 100% Gratuita):**
   * Subí tu proyecto a un repositorio en **GitHub**.
   * Ingresá a [share.streamlit.io](https://share.streamlit.io) con tu cuenta de GitHub.
   * Seleccioná el repositorio y el archivo principal `app.py`.
   * En 2 minutos se creará una URL pública (ejemplo: `https://caps-gianotti-oroverde.streamlit.app`) que podés compartir con compañeros, docentes de la cátedra o vecinos.

2. **Acceso en Red Local (WiFi de la Facultad o CAPS - Sin costo):**
   * Podés ejecutar la app permitiendo conexiones desde otros dispositivos en la misma red WiFi:
     ```powershell
     streamlit run app.py --server.address 0.0.0.0 --server.port 8501
     ```
   * En cualquier celular o notebook conectado al mismo WiFi, ingresan escribiendo tu IP local (ejemplo: `http://192.168.1.45:8501`).

3. **Túnel Temporal Gratuito (ngrok / Localtunnel):**
   * Ideal para una defensa o presentación en vivo sin configurar servidores:
     ```powershell
     npx localtunnel --port 8501
     ```
   * Te generará un enlace público temporal para enviar por WhatsApp al jurado de la cátedra.

