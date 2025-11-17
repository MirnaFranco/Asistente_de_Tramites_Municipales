from langchain_community.document_loaders import PyPDFLoader
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# --- Configuración ---
load_dotenv()
api_key = os.getenv("API_KEY")
carpeta = "./tramites"

if not api_key:
    raise ValueError("⚠️ API_KEY no está definido en el archivo .env")

# --- Funciones de Carga y División ---

def upload_pdf(path: str):
    """Carga y concatena el contenido de un PDF"""
    try:
        loader = PyPDFLoader(path)
        pages = loader.load()
        text = "\n".join([p.page_content for p in pages])
        return text
    except Exception as e:
        print(f"❌ Error al cargar PDF {path}: {e}")
        return ""

def split_text(text: str, archivo: str):
    """Divide el texto en fragmentos para indexar"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    docs = splitter.create_documents([text])
    for doc in docs:
        doc.metadata = {"source": archivo}  # ✅ Mejora: agregar metadatos únicos
    print(f"✅ {len(docs)} fragmentos creados.")
    return docs

# --- Funciones de Embedding y Vector Store ---

embedding = OllamaEmbeddings(model="nomic-embed-text:latest")

def get_vector_store(name_collection: str):
    vector_store = Chroma(
        collection_name=name_collection,
        embedding_function=embedding,
        persist_directory="./vectorstore"
    )
    return vector_store

# --- Función de Recuperación ---

def retrieval(input_user: str):
    vector_store = get_vector_store("tramites_formosa")
    docs = vector_store.similarity_search(input_user, k=5)
    return docs

# --- Configuración y Función de Respuesta LLM ---

prompt = PromptTemplate.from_template("""
Eres un asistente encargado de responder preguntas sobre trámites de la municipalidad de Formosa.
Usa exclusivamente la información del contexto para responder al usuario.
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
    for chunk in llm.stream(prompt.format(contexto=contexto, input_user=input_user)):
        yield chunk.content

# ===============================================
## 🚀 Fase de Indexación
# ===============================================

print("\n--- INICIANDO FASE DE INDEXACIÓN ---")

vector_store = get_vector_store("tramites_formosa")
archivos_indexados = set(os.listdir("./vectorstore/tramites_formosa")) if os.path.exists("./vectorstore/tramites_formosa") else set()

for archivo in os.listdir(carpeta):
    if archivo.endswith(".pdf") and archivo not in archivos_indexados:
        ruta = os.path.join(carpeta, archivo)
        print(f"📄 Leyendo: {archivo}")

        try:
            loader = PyPDFLoader(ruta)
            pages = loader.load()
            text = "\n".join([p.page_content for p in pages])

            if text.strip():
                docs = split_text(text, archivo)

                if docs:
                    vector_store.add_documents(docs)
                    print(f"💾 Fragmentos de {archivo} guardados en ChromaDB.")
                else:
                    print(f"⚠️ El archivo {archivo} se cargó, pero no generó fragmentos.")
            else:
                print(f"⚠️ El archivo {archivo} no contiene texto útil.")

        except Exception as e:
            print(f"❌ Error al procesar {archivo}: {type(e).__name__} - {e}")

print("--- INDEXACIÓN COMPLETADA ---\n")

# ===============================================
## 💬 Fase de Consulta
# ===============================================

while True:
    input_user = input("❓ Pregunta sobre trámites (o 'salir'): ")
    if input_user.lower() == "salir":
        break

    docs = retrieval(input_user=input_user)

    if docs:
        contexto = "\n".join([doc.page_content for doc in docs])
        print("\n💬 Asistente:")
        for chunk in response(input_user=input_user, contexto=contexto):
            print(chunk, end="", flush=True)
        print("\n")
    else:
        print("⚠️ No se encontraron documentos relevantes.")