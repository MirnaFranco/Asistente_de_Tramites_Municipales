# Asistente Inteligente de Trámites Municipales – Formosa
Un sistema de consulta automatizada que permite a ciudadanos y empleados municipales acceder rápidamente a información sobre trámites públicos, utilizando inteligencia artificial y búsqueda semántica sobre documentos PDF oficiales.

## Descripción del Problema
En muchas municipalidades, la información sobre trámites está dispersa en documentos PDF, sin buscadores eficientes ni interfaces amigables. Esto genera demoras, confusión y dependencia de atención presencial.
Este proyecto soluciona ese problema permitiendo:
• 	Indexar automáticamente documentos oficiales.
• 	Consultar por lenguaje natural (ej. “¿Dónde tramito mi licencia?”).
• 	Obtener respuestas claras, contextualizadas y con referencias.
Destinado a: ciudadanos, empleados administrativos, desarrolladores de soluciones cívicas.

## Instrucciones de Instalación
 1. Clonar el repositorio
```
git clone https://github.com/tu-usuario/Tramites-Municipales-RAG.git 

cd asistente-tramites-formosa
```

 2. Crear entorno virtual (opcional pero recomendado)
```
python -m venv env
source env/bin/activate  # En Windows: .\env\Scripts\activate
```
 3. Instalar dependencias

```
pip install -r requirements.txt
```
 4. Configurar clave de API
```
echo "API_KEY=tu_clave_de_gemini" > .env
```
## Instrucciones de Uso
```
python main.py
```
- Carga automáticamente los PDFs desde .
- Indexa los fragmentos en ChromaDB.
- Permite consultas por texto en consola.
## Estructura del Proyecto
```
├── tramites/                  # Carpeta con PDFs a indexar
├── vectorstore/              # Persistencia de ChromaDB
├── .env                      # API_KEY para Gemini
├── main.py                   # Script principal
```
## Requisitos
• 	Python 3.10+
• 	Ollama instalado y corriendo localmente
• 	 con tu clave de API de Gemini:
```
API_KEY=tu_clave_de_api
```

## Tecnologías Usadas
- LangChain: Orquestación de carga, embeddings y consulta.
- Ollama: Generación de embeddings (nomic-embed-text).
- ChromaDB: Almacenamiento vectorial persistente.
- Gemini SDK: Generación de respuestas contextuales.
- PyPDFLoader: Extracción de texto desde PDFs.
- TextSplitter: División en fragmentos para indexación
- Dotenv: Manejo seguro de claves API

### Fase de Indexación
1. 	Carga todos los PDFs desde .
2. 	Extrae el texto y lo divide en fragmentos de 1500 caracteres con solapamiento.
3. 	Genera embeddings y los guarda en ChromaDB con metadatos del archivo fuente.


### Fase de Consulta
Una vez indexado, el sistema permite realizar preguntas sobre trámites:

El sistema:
• 	Recupera los 5 fragmentos más relevantes.
• 	Genera una respuesta clara y concisa usando Gemini.
• 	Muestra la respuesta en consola.

## Buenas Prácticas Implementadas
• 	Validación de API_KEY y PDFs vacíos
• 	Manejo de errores con 
• 	Metadatos por fragmento ()
• 	Separación modular por función
• 	Indexación incremental (evita duplicados)

## Ideas Futuras
• 	Interfaz web con Streamlit o Gradio
• 	Clasificación por tipo de trámite
• 	Búsqueda híbrida por texto + metadatos
• 	Exportación de respuestas a PDF o Markdown