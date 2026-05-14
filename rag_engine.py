import os
from urllib.parse import urlparse

from google import genai
from google.genai import types
from dotenv import load_dotenv
from vector_store import query_db

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# ─── Sistem Talimatları (System Instruction) ─────────────────────────────────
SYSTEM_INSTRUCTION = """
Sen uzman bir Optisyenlik ve Göz Sağlığı Asistanısın. Görevin, optik mağazacılık, 
göz hastalıkları, kırma kusurları, gözlük camı teknolojileri ve Türkiye'deki 
optisyenlik mevzuatı (5193 sayılı kanun vb.) hakkında kullanıcılara doğru, 
bilimsel ve güncel bilgiler sunmaktır.

ÇALIŞMA PRENSİPLERİ:
- ADIM ADIM DÜŞÜN: Kullanıcı sorusunu aldığında önce hangi uzmanlık alanına (klinik, teknik, mevzuat) girdiğini analiz et.
- ZORUNLU ARAÇ KULLANIMI: Kendi dahili bilgine güvenme! Teknik, klinik veya hukuki her soruda İLK İŞ OLARAK MUTLAKA 'search_optician_knowledge' aracını kullan.
- BİLGİ SENTEZİ: Gelen bağlamı (context) analiz et ve soruyu doğrudan yanıtla.
- DİLLER ARASI SENTEZ: Kaynak dökümanlar İngilizce olsa bile teknik terimleri koruyarak profesyonel TÜRKÇE yanıt ver.

KISITLAMALAR:
- Tıbbi reçete veya ilaç tavsiyesi yapma.
- Teşhis koyma; yalnızca dökümanlardaki bilimsel verileri raporla.
- Dökümanlarda bulunmayan bilgiyi uydurma (Halüsinasyon yapma).

ÇIKTI FORMATI:
Yanıtını profesyonel bir dille sun. Sonunda mutlaka 'Teknik dökümanlara dayalı analizim budur.' ifadesini kullan.
"""

# ─── Modül düzeyinde kaynak akümülatörü ─────────────────────────────────────
_accumulated_sources: list = []

def _reset_sources() -> None:
    global _accumulated_sources
    _accumulated_sources = []

def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc or url
    except Exception:
        return url

# ─── ARAÇ: Semantik Arama ───────────────────────────────────────────────────
def search_optician_knowledge(query: str) -> str:
    """
    Optisyenlik mevzuatı, teknik optik ve klinik konular hakkında 
    veritabanında semantik arama yapar.
    """
    global _accumulated_sources

    # Terminalde Gemini'ın aracı kullandığını görmek için kontrol çıktısı
    print(f"🔍 [SİSTEM] Gemini Veritabanında Arıyor: '{query}'")

    res = query_db(query)

    if not res["documents"] or not res["documents"][0]:
        return "Teknik veritabanında bu konuyla ilgili spesifik bir döküman bulunamadı."

    metadatas     = res.get("metadatas", [[]])[0] or []
    context_parts: list[str] = []

    for doc, meta in zip(res["documents"][0], metadatas):
        # Kaynak adresini güvenli şekilde
        url     = meta.get("source", "").strip()
        section = meta.get("section", "Bilinmeyen Bölüm").strip()
        domain  = _domain(url)

        entry = {"url": url, "section": section, "domain": domain}
        if url and entry not in _accumulated_sources:
            _accumulated_sources.append(entry)
            print(f"    ✓ Kaynak eklendi: {domain} — {section[:40]}")

        context_parts.append(f"[{domain} | {section}]\n{doc}")

    return "\n---\n".join(context_parts)

def get_optirag_response(user_query: str) -> tuple[str, list]:
    """
    (yanıt_metni, kaynaklar_listesi) döndürür.
    kaynaklar_listesi: [{"url": ..., "section": ..., "domain": ...}, ...]
    """
    _reset_sources()
    print(f"\n🔍 Soru işleniyor: {user_query[:60]}...")

    # Önce yerel veritabanında bu soruya ilişkin geçerli kaynak var mı kontrol et.
    precheck = search_optician_knowledge(user_query)
    if not _accumulated_sources:
        print("⚠️  Kaynak bulunamadı, sistemde böyle bir bilgi yok.")
        return "Sistemde böyle bir bilgi bulunmamaktadır.", []

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[search_optician_knowledge],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(),
            ),
        )

        answer  = response.text.strip() if response.text else "Yanıt oluşturulamadı."
        sources = list(_accumulated_sources)
        print(f"✅ Cevap oluşturuldu. Kaynaklar: {len(sources)} adet")
        for src in sources:
            print(f"   📌 {src.get('domain', 'Bilinmeyen')} — {src.get('section', 'Bilinmeyen Bölüm')[:50]}")
        return answer, sources

    except Exception as e:
        if "429" in str(e):
            return "❌ Kota sınırı aşıldı. Lütfen 1 dakika sonra tekrar deneyin.", []
        return f"❌ OptiRAG Sistem Hatası: {str(e)}", []