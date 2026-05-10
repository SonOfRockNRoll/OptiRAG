import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from vector_store import query_db

# Çevresel değişkenleri yükle
load_dotenv()

# Google GenAI istemcisini başlat
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# --- HAFTA 9: ARAÇ TANIMLAMA (TOOL CALLING) ---
def search_optician_knowledge(query: str):
    """
    Optisyenlik mevzuatı (5193 sayılı kanun), teknik optik (progresif camlar, kaplamalar) 
    ve klinik konular (miyopi, hipermetropi, katarakt, keratokonus vb.) hakkında 
    geniş teknik veritabanında semantik arama yapar.
    """
    # Vektör veritabanından en alakalı dökümanları getirir
    res = query_db(query)
    
    if not res['documents'] or not res['documents'][0]:
        return "Teknik veritabanında bu konuyla ilgili spesifik bir döküman bulunamadı."

    # Getirilen parçaları (chunks) birleştirerek bağlam oluşturur
    context = "\n---\n".join(res['documents'][0])
    return context

# --- HAFTA 7: GELİŞMİŞ SİSTEM TALİMATI (PROMPT ENGINEERING) ---
SYSTEM_INSTRUCTION = """
# ROL VE UZMANLIK
Sen 'OptiRAG' adında, optisyenlik alanında akademik, teknik ve hukuki derinliği olan uzman bir yapay zeka ajanısın.

# YETKİ VE BİLGİ ALANLARIN
1. KLİNİK: Miyopi, Hipermetropi, Astigmatizma, Presbiyopi, Glokom, Katarakt ve Kornea hastalıkları.
2. TEKNİK: Cam kaplama teknolojileri (Anti-refle, Mavi ışık, Polarize), Progresif ve Bifokal lensler, optik fizik.
3. HUKUKİ: 5193 Sayılı Optisyenlik Hakkında Kanun, yönetmelikler ve mağaza standartları.

# ÇALIŞMA PRENSİPLERİ (H7 CoT & H9 ReAct)
- ADIM ADIM DÜŞÜN: Kullanıcı sorusunu aldığında önce hangi uzmanlık alanına girdiğini analiz et.
- AKTİF ARAŞTIRMA: Teknik veya hukuki her türlü soruda MUTLAKA 'search_optician_knowledge' aracını kullan.
- DİLLER ARASI SENTEZ: Kaynak dökümanlar İngilizce (EyeWiki gibi) olsa bile, teknik terimleri koruyarak profesyonel bir TÜRKÇE ile yanıt ver.
- KISITLAMALAR VE ETİK:
    - Kesinlikle tıbbi reçete hazırlama veya ilaç tavsiye etme.
    - Teşhis koyma; sadece dökümanlardaki bilimsel ve teknik verileri raporla.
    - Dökümanlarda bulunmayan bilgiyi uydurma (Halüsinasyon engelleme).

# ÇIKTI FORMATI
Yanıtlarını profesyonel bir dille sun ve sonunda mutlaka 'Teknik dökümanlara dayalı analizim budur.' ifadesini kullan.
"""

def get_optirag_response(user_query):
    """
    Kullanıcı sorgusunu alır, ajanı yönetir ve sonucu döndürür.
    """
    try:
        # Ajanın kullanabileceği araçlar
        tools = [search_optician_knowledge]

        # Gemini 1.5 Flash üzerinden Agentic Yapılandırma
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=tools,
                # Otomatik fonksiyon çağırma (ReAct döngüsü) aktif
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
            )
        )

        # Ajanın ürettiği nihai metin
        answer = response.text.strip()
        
        # Kaynak meta verisi (Ajan otomatik yönettiği için genel bilgi döner)
        sources = [{"section": "Dinamik Ajan Sentezi", "source": "Genişletilmiş OptiRAG Veritabanı"}]
        
        return answer, sources

    except Exception as e:
        # Hata durumunda kullanıcı dostu mesaj
        if "429" in str(e):
            return "❌ Kota sınırı aşıldı. Lütfen 1 dakika sonra tekrar deneyin.", []
        return f"❌ OptiRAG Sistem Hatası: {str(e)}", []