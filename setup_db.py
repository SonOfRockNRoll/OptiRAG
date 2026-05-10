from scraper import scrape_optical_sites
from vector_store import create_vector_db
import os

def initialize():
    # TEMEL VE KRİTİK KAYNAKLAR (Stabilite için rafine edildi)
    urls = [
        # 1. Klinik Derinlik (İngilizce Akademik)
        "https://eyewiki.aao.org/Keratoconus",
        
        # 2. Teknik Optik (Cam Teknolojileri)
        "https://www.optikgazete.com/teknik-optik/gozluk-camlarinda-kaplamalar-ve-ozellikleri-h123.html",
        
        # 3. Mevzuat (Yasal Çerçeve)
        "https://www.optisyeninsesi.com/haberler/5193-sayili-optisyenlik-hakkinda-kanun-ve-yonetmeligi-h15203.html",
        
        # 4. Genel Kırma Kusurları
        "https://eyewiki.aao.org/Myopia"
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