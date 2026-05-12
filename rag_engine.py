import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from vector_store import query_db

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# --- KAYNAK TAKİP LİSTESİ ---
# Ajanın arama yaparken bulduğu URL'leri burada biriktireceğiz
current_retrieved_sources = []

def search_optician_knowledge(query: str):
    """
    Optisyenlik veritabanında arama yapar ve bulunan kaynakları listeye ekler.
    """
    global current_retrieved_sources
    res = query_db(query)
    
    if not res['documents'] or not res['documents'][0]:
        return "Teknik veritabanında bu konuyla ilgili döküman bulunamadı."

    # Metadatalar içindeki 'source' (URL) bilgisini ayıklayıp listeye ekle
    if 'metadatas' in res and res['metadatas'] and res['metadatas'][0]:
        for meta in res['metadatas'][0]:
            source_url = meta.get('source')
            if source_url and source_url not in current_retrieved_sources:
                current_retrieved_sources.append(source_url)

    context = "\n---\n".join(res['documents'][0])
    return context

SYSTEM_INSTRUCTION = """
Sen 'OptiRAG' adında uzman bir asistansın. 
Teknik veya hukuki her türlü soruda MUTLAKA 'search_optician_knowledge' aracını kullan.
Cevaplarını profesyonel bir dille sun ve sonunda mutlaka 'Teknik dökümanlara dayalı analizim budur.' ifadesini kullan.
"""

def get_optirag_response(user_query):
    global current_retrieved_sources
    current_retrieved_sources = [] # Her yeni soruda listeyi sıfırla
    
    try:
        tools = [search_optician_knowledge]

        response = client.models.generate_content(
            model='gemini-flash-latest', # En güncel ve stabil model ismin
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
            )
        )

        answer = response.text.strip() if response.text else "Yanıt oluşturulamadı."
        
        # --- DİNAMİK KAYNAK OLUŞTURMA ---
        # Eğer ajan döküman kullandıysa, yakaladığımız URL'leri listeye çeviriyoruz
        if current_retrieved_sources:
            sources = [{"section": "Kaynak Doküman", "source": url} for url in current_retrieved_sources]
        else:
            # Eğer ajan dökümana bakmadan genel bilgiyle cevap verdiyse
            sources = [{"section": "Genel Bilgi", "source": "Modelin genel eğitim verileri"}]
        
        return answer, sources

    except Exception as e:
        if "429" in str(e):
            return "❌ Kota sınırı aşıldı. Lütfen biraz bekleyin.", []
        return f"❌ Sistem Hatası: {str(e)}", []