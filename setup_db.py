from scraper import scrape_optical_sites
from vector_store import create_vector_db
import os

def initialize():
    urls = [
        # ============================================================
        # --- KLİNİK OTORİTE (EyeWiki - AAO) --- [Doğrulanmış: 200 OK]
        # ============================================================
        # Kırma kusurları
        "https://eyewiki.aao.org/Myopia",
        "https://eyewiki.aao.org/Hyperopia",
        "https://eyewiki.aao.org/Astigmatism",
        "https://eyewiki.aao.org/Presbyopia",
        "https://eyewiki.aao.org/Keratoconus",
        # Göz hastalıkları
        "https://eyewiki.aao.org/Glaucoma",
        "https://eyewiki.aao.org/Normal_Tension_Glaucoma",
        "https://eyewiki.aao.org/Ocular_Hypertension",
        "https://eyewiki.aao.org/Cataract",
        "https://eyewiki.aao.org/Retinal_Detachment",
        "https://eyewiki.aao.org/Diabetic_Retinopathy",
        "https://eyewiki.aao.org/Age-Related_Macular_Degeneration",
        "https://eyewiki.aao.org/Retinitis_Pigmentosa",
        "https://eyewiki.aao.org/Conjunctivitis",
        "https://eyewiki.aao.org/Blepharitis",
        "https://eyewiki.aao.org/Pterygium",
        # Göz kası / pediatri
        "https://eyewiki.aao.org/Amblyopia",
        "https://eyewiki.aao.org/Esotropia",
        "https://eyewiki.aao.org/Exotropia",
        "https://eyewiki.aao.org/Nystagmus",
        "https://eyewiki.aao.org/Pseudoexfoliation_Syndrome",
        # Kontakt lens ve optik araç
        "https://eyewiki.aao.org/Contact_Lenses",
        "https://eyewiki.aao.org/Prism",
        "https://eyewiki.aao.org/Corneal_Topography",
        "https://eyewiki.aao.org/Optical_Coherence_Tomography",

        # ============================================================
        # --- TEKNİK OPTİK (Wikipedia) --- [Doğrulanmış: 200 OK]
        # ============================================================
        # Kaplama teknolojileri
        "https://en.wikipedia.org/wiki/Anti-reflective_coating",
        "https://en.wikipedia.org/wiki/Photochromic_lens",
        "https://en.wikipedia.org/wiki/Polarized_light",
        # Cam ve lens teknolojisi
        "https://en.wikipedia.org/wiki/Progressive_lens",
        "https://en.wikipedia.org/wiki/Bifocal_lens",
        "https://en.wikipedia.org/wiki/Corrective_lens",
        "https://en.wikipedia.org/wiki/Contact_lens",
        "https://en.wikipedia.org/wiki/Lens_(optics)",
        "https://en.wikipedia.org/wiki/Refractive_index",
        "https://en.wikipedia.org/wiki/Optical_aberration",
        # Mavi ışık
        "https://en.wikipedia.org/wiki/Blue_light",

        # ============================================================
        # --- MEVZUAT (Resmi Kaynaklar) --- [setup_db'ye ek; add_mevzuat.py de çalışır]
        # ============================================================
        "https://www.resmigazete.gov.tr/eskiler/2004/07/20040714.htm",
        "https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5193&MevzuatTur=1&MevzuatTertip=5",
    ]
    
    print("🚀 OptiRAG Veri Kurulumu Başladı...")
    print(f"🌐 {len(urls)} kritik kaynak taranıyor...")
    
    all_data = scrape_optical_sites(urls)
    
    if all_data:
        # Eski veritabanı kalıntılarını temizlemek için opsiyonel:
        # if os.path.exists("./opti_db"):
        #     print("🧹 Eski veritabanı temizleniyor...")
        
        create_vector_db(all_data)
        print(f"✨ Başarılı! {len(all_data)} bilgi parçası MacBook'a işlendi.")
        print("💡 'streamlit run app.py' yazarak asistanı başlatabilirsin.")
    else:
        print("❌ Veri toplanamadı. İnternet bağlantısını kontrol edin.")

if __name__ == "__main__":
    initialize()