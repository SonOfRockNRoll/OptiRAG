"""
5193 Sayılı Optisyenlik Hakkında Kanun ve Yönetmelik metinlerini
ChromaDB'ye statik olarak ekler.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vector_store import create_vector_db

MEVZUAT_URL = "https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=5193&MevzuatTur=1&MevzuatTertip=5"
YONETMELIK_URL = "https://www.resmigazete.gov.tr/eskiler/2004/07/20040714.htm"

mevzuat_data = [
    {
        "url": MEVZUAT_URL,
        "section": "5193 Sayılı Kanun - Genel",
        "text": (
            "5193 Sayılı Optisyenlik Hakkında Kanun, 11 Haziran 2004 tarihinde yürürlüğe girmiştir. "
            "Bu Kanun, optisyenlerin mesleki yeterliliklerini, optisyenlik müesseselerinin açılış "
            "koşullarını ve denetim esaslarını düzenlemektedir. Kanun kapsamında optisyenlik "
            "müessesesi; gözlük, lens ve benzeri görme araçlarının satışının yapıldığı, "
            "gözlük camı montajının gerçekleştirildiği işyerini ifade eder."
        )
    },
    {
        "url": MEVZUAT_URL,
        "section": "5193 Sayılı Kanun - Ruhsatlandırma Şartları",
        "text": (
            "Optisyenlik müessesesi açmak için İl Sağlık Müdürlüğü'nden ruhsat alınması zorunludur. "
            "Ruhsat başvurusunda asgari alan şartlarının sağlandığına dair belgeler sunulmalıdır. "
            "Ruhsatlandırma aşamasında İl Sağlık Müdürlükleri tarafından denetim yapılmaktadır. "
            "Optisyenlik müessesesi yalnızca diplomalı optisyen tarafından açılabilir ve işletilebilir."
        )
    },
    {
        "url": YONETMELIK_URL,
        "section": "Yönetmelik Madde 16 - Asgari Fiziki Şartlar",
        "text": (
            "Optisyenlik Müesseseleri Hakkında Yönetmelik Madde 16 uyarınca, bir optisyenlik "
            "müessesesinin asgari fiziki şartları şunlardır: "
            "Toplam kullanım alanı, personel alanı ve atölye dahil olmak üzere en az 25 metrekare "
            "olmak zorundadır. "
            "Müessese; satış alanı ve gözlük camı montajının yapıldığı atölye (laboratuvar) olmak "
            "üzere en az iki ana bölümden oluşmalıdır. "
            "Tavan yüksekliği tabandan tavana en az 2,40 metre olmalıdır. "
            "Atölye bölümü, teknik işlemlerin yürütülebileceği uygun genişlikte olmalı, "
            "yeterli aydınlatma ve havalandırma sağlanmalıdır."
        )
    },
    {
        "url": YONETMELIK_URL,
        "section": "Yönetmelik - Atölye (Laboratuvar) Gereksinimleri",
        "text": (
            "Optisyenlik müesseselerinde atölye (laboratuvar) bölümünde bulunması gereken ekipmanlar: "
            "Gözlük camı traşlama makinesi (bikonkav, bikonveks ve silindirik camları işleyebilir nitelikte), "
            "lensmetre (cam gücünü ölçen cihaz), santraj cetveli, "
            "cam kesme aleti ve gerekli el aletleri bulunmalıdır. "
            "Atölye alanı; cam traşlama, montaj ve kalite kontrol işlemlerini rahatça yürütmeye "
            "elverişli biçimde düzenlenmiş olmalıdır."
        )
    },
    {
        "url": YONETMELIK_URL,
        "section": "Yönetmelik - Satış Alanı ve Müşteri Hizmetleri",
        "text": (
            "Optisyenlik müessesesinin satış alanında; gözlük çerçeveleri ve camları için uygun "
            "vitrin ve teşhir dolapları bulunmalıdır. "
            "Göz ölçüm işlemleri için gerekli ekipmanlar (otorefrakter veya muayene koltuğu gibi) "
            "mevcutsa, bu alan satış alanından ayrı düzenlenebilir. "
            "Müşteri bekleme alanı ile kasiyerlik hizmetine uygun bir tezgah veya masa zorunludur."
        )
    },
    {
        "url": MEVZUAT_URL,
        "section": "5193 Sayılı Kanun - Optisyen Yetki ve Sorumlulukları",
        "text": (
            "5193 Sayılı Kanun kapsamında optisyenler şu işlemleri yapmaya yetkilidir: "
            "Gözlük reçetesine göre cam ve çerçeve satışı yapmak, "
            "gözlük camı traşlama ve montaj işlemi gerçekleştirmek, "
            "kontakt lens satışı yapmak (reçete aranır). "
            "Optisyenler göz muayenesi yapamazlar; bu işlem yalnızca göz hekimleri tarafından yapılabilir. "
            "Optisyen diploması, 4 yıllık optisyenlik-gözlükçülük bölümü mezuniyetine dayanmalıdır."
        )
    },
]

if __name__ == "__main__":
    print("📜 Mevzuat verileri ChromaDB'ye ekleniyor...")
    create_vector_db(mevzuat_data)
    print("✅ Mevzuat verileri başarıyla eklendi!")
