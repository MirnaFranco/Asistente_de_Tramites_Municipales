from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Dependencias de LangChain (Asumiendo que las funciones ya existen en tu proyecto)
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from fastapi.middleware.cors import CORSMiddleware

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("API_KEY")

# --- Configuración y Funciones RAG (DEBEN ESTAR COPIADAS DE TU index.py) ---

# 1. Configuración de Embedding (Ollama)
try:
    embedding = OllamaEmbeddings(model="nomic-embed-text:latest")
except Exception as e:
    # Si Ollama no está activo, la API fallará al iniciar la DB.
    # Pero lo dejamos así por simplicidad.
    print(f"❌ ADVERTENCIA: Ollama no configurado correctamente. {e}")
    # Considera una inicialización perezosa si esto da problemas.


# 2. Funciones RAG
def get_vector_store(name_collection: str): 
    # Asegúrate de que el persist_directory sea accesible.
    vector_store = Chroma(
        collection_name=name_collection,
        embedding_function=embedding,
        persist_directory="./vectorstore"
    )
    return vector_store

def retrieval(input_user: str): 
    # La DB DEBE ESTAR INDEXADA PREVIAMENTE
    vector_store = get_vector_store("tramites_formosa")
    docs = vector_store.similarity_search(input_user, k=5) 
    return docs

prompt = PromptTemplate.from_template("""
    Eres un asistente encargado de responder preguntas sobre tramites de la municipalidad de Formosa.
    Usa exclusivamente la informacion del contexto para responder al usuario.
    contexto = {contexto}
    pregunta del usuario: {input_user}
                                    
    Responde de forma clara y concisa, mencionando sedes o direcciones si aplica.
""")

def response(input_user: str, contexto: str):
    llm = ChatGoogleGenerativeAI(
        api_key=api_key,
        model="gemini-2.5-flash",
        temperature=0.4
    )
    # Generación normal (no stream) para una respuesta API
    result = llm.invoke(prompt.format(contexto=contexto, input_user=input_user))
    return result.content


# ----------------------------------------------------
# 3. Inicialización del Servidor FastAPI
# ----------------------------------------------------

app = FastAPI(
    title="Asistente RAG de Trámites de Formosa",
    description="API para consultar documentos indexados con Gemini y Ollama."
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # En producción usar dominio específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Definir el esquema de datos para la solicitud (payload)
class Query(BaseModel):
    query: str

# ----------------------------------------------------
# 4. Endpoints
# ----------------------------------------------------

@app.post("/consultar-tramites")
def query_rag_system(data: Query):
    """
    Endpoint principal para enviar una pregunta y obtener una respuesta del RAG.
    """
    try:
        input_user = data.query
        
        # 1. Recuperación (Retrieval)
        docs = retrieval(input_user=input_user)
        
        if not docs or not docs[0].page_content.strip():
            # Si no se encuentra contexto relevante, devuelve un mensaje específico.
            return {
                "response": "Lo siento, no tengo información relevante en la base de datos para responder a esa pregunta.",
                "context": []
            }
        
        # 2. Preparar el Contexto
        contexto = "\n".join([doc.page_content for doc in docs])
        
        # Opcional: Extraer los metadatos para saber las fuentes
        sources = [
            {"content": doc.page_content, "source": doc.metadata.get('source'), "page": doc.metadata.get('page_label')}
            for doc in docs
        ]

        # 3. Generación (Generation)
        respuesta_llm = response(input_user=input_user, contexto=contexto)
        
        return {
            "response": respuesta_llm,
            "context_sources": sources
        }
    
    except Exception as e:
        # Manejo de errores internos (ej: falla de Ollama/Gemini)
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno del servidor al procesar la consulta: {str(e)}"
        )