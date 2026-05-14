# OptiRAG: Akıllı Optisyenlik Asistanı 👓

Bu proje, **İSTE Mühendislikte Bilgisayar Uygulamaları II** dersi kapsamında geliştirilmiş bir **Agentic RAG (Retrieval-Augmented Generation)** sistemidir. Optisyenlik öğrencileri ve profesyonelleri için klinik, teknik ve hukuki konularda güvenilir, halüsinasyon yapmayan (sıfır uydurma) ve anlık kaynak gösteren bir yapay zeka asistanı olarak tasarlanmıştır.

### 🌟 Özellikler ve Gelişim Süreci
* **Hafta 7:** Gelişmiş Prompt Engineering ve Sistem Talimatlarının (System Instructions) oluşturulması.
* **Hafta 8:** ChromaDB ile Vektör Veritabanı kurulumu ve akademik otoritelerden (EyeWiki) Web Scraping ile veri toplanması.
* **Hafta 9:** Agentic AI yapısı ile dinamik araç kullanımı (Function Calling).
* **Hafta 10 & 11 (Final):** **T.C. Optisyenlik Mevzuatı (5193 Sayılı Kanun)** entegrasyonu, hata toleransı (Exponential Backoff) ve dinamik tıklanabilir kaynak gösterimi.

### 🛠️ Kullanılan Teknolojiler
* **LLM & Embedding:** Google Gemini API / `gemini-embedding-001`
* **Vektör Veritabanı:** ChromaDB (Kalıcı / Persistent)
* **Arayüz:** Streamlit
* **Veri Toplama:** BeautifulSoup4, Requests

### 🚀 Kurulum ve Çalıştırma

Sistemin "Klinik" ve "Hukuki" hafızasını doğru bir şekilde oluşturmak için sırasıyla aşağıdaki adımları izleyiniz:

**1. Gerekli kütüphaneleri yükleyin:**
```bash
pip install -r requirements.txt
#Database yükler
python3 setup_db.py
#Mevzuat gömülü durumda olduğu için onu da database ekle
python3 add_mevzuat.py
#arayüzü çalıştır
streamlit run app.py