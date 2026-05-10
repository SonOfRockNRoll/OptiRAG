import os
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
EMBED_MODEL = "gemini-embedding-001" 

def create_vector_db(scraped_data):
    # MacBook dosya yolları için güvenli klasörleme
    chroma_client = chromadb.PersistentClient(path="./opti_db")
    collection = chroma_client.get_or_create_collection(name="optirag_knowledge")

    print(f"🧠 {len(scraped_data)} veri parçası vektörize ediliyor...")

    for i, entry in enumerate(scraped_data):
        try:
            result = client.models.embed_content(
                model=EMBED_MODEL,
                contents=entry['text']
            )
            
            collection.add(
                ids=[f"id_{i}"],
                embeddings=[result.embeddings[0].values],
                documents=[entry['text']],
                metadatas=[{"source": entry['url'], "section": entry['section']}]
            )
        except Exception as e:
            print(f"❌ Vektör hatası (id_{i}): {e}")
    print("✅ Vektör veritabanı başarıyla oluşturuldu.")

def query_db(query_text, n_results=3):
    chroma_client = chromadb.PersistentClient(path="./opti_db")
    collection = chroma_client.get_collection(name="optirag_knowledge")
    
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=query_text
    )
    
    return collection.query(
        query_embeddings=[result.embeddings[0].values],
        n_results=n_results
    )