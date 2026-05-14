import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}
MIN_CHUNK_LEN = 150    # bir chunk'ın min karakter uzunluğu
MAX_CHUNK_LEN = 2000   # bir chunk'ın max karakter uzunluğu

# Vektör DB'ye eklenmeyecek boilerplate Wikipedia bölümleri
SKIP_SECTIONS = {
    'references', 'external links', 'see also', 'further reading',
    'notes', 'bibliography', 'footnotes', 'contents',
    'kaynakça', 'ayrıca bakınız', 'dış bağlantılar',
}


def _clean_text(text: str) -> str:
    """Gereksiz boşluk, edit linkleri ve referans numaralarını temizler."""
    text = re.sub(r'\[edit\]|\[Edit\]', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _add_chunks(data: list, url: str, section: str, text: str) -> None:
    """
    Uzun metni MAX_CHUNK_LEN'e bölerek data listesine ekler.
    Bölüm birden fazla parçaya bölünürse etiket '(devam X)' olarak eklenir.
    """
    words = text.split()
    chunk = ""
    part = 1
    for word in words:
        chunk += word + " "
        if len(chunk) >= MAX_CHUNK_LEN:
            cleaned = chunk.strip()
            if len(cleaned) >= MIN_CHUNK_LEN:
                label = section if part == 1 else f"{section} (devam {part})"
                data.append({"url": url, "section": label, "text": cleaned})
                part += 1
            chunk = ""
    # Kalan metin
    cleaned = chunk.strip()
    if len(cleaned) >= MIN_CHUNK_LEN:
        label = section if part == 1 else f"{section} (devam {part})"
        data.append({"url": url, "section": label, "text": cleaned})


def _scrape_wikipedia(url: str, soup: BeautifulSoup) -> list:
    """
    Wikipedia için: h2/h3 başlıklarını section adı olarak kullanır.
    Boilerplate bölümleri (References, See Also vb.) atlar.
    """
    data = []

    # Sayfa başlığı
    title_tag = soup.find('h1', id='firstHeading')
    page_title = (
        title_tag.get_text().strip()
        if title_tag
        else url.split('/')[-1].replace('_', ' ')
    )

    content_div = soup.find('div', class_='mw-parser-output')
    if not content_div:
        return data

    current_section = page_title   # Herhangi bir başlık gelmeden önceki giriş paragrafları
    current_text    = ""

    for element in content_div.children:
        if not hasattr(element, 'name') or not element.name:
            continue

        if element.name in ('h2', 'h3'):
            # Önceki bölümü kaydet
            if current_text.strip():
                _add_chunks(data, url, current_section, current_text)

            raw_heading   = _clean_text(element.get_text())
            # Boilerplate bölümleri atla
            if raw_heading.lower() in SKIP_SECTIONS:
                current_section = "__SKIP__"
                current_text    = ""
                continue

            current_section = f"{page_title} — {raw_heading}"
            current_text    = ""

        elif element.name == 'p' and current_section != "__SKIP__":
            txt = _clean_text(element.get_text())
            if len(txt) > 30:
                current_text += txt + " "

    # Son bölümü kaydet
    if current_text.strip() and current_section != "__SKIP__":
        _add_chunks(data, url, current_section, current_text)

    return data


def _scrape_eyewiki(url: str, soup: BeautifulSoup) -> list:
    """
    EyeWiki / genel mediawiki yapısı: h2/h3 başlıkları → kardeş p tagları.
    """
    data = []
    for header in soup.find_all(['h2', 'h3']):
        section_title = _clean_text(header.get_text())
        if not section_title or len(section_title) > 120:
            continue
        if section_title.lower() in SKIP_SECTIONS:
            continue

        content = ""
        for sibling in header.find_next_siblings():
            if sibling.name in ['h1', 'h2', 'h3']:
                break
            if sibling.name == 'p':
                content += sibling.get_text().strip() + " "
            elif sibling.name == 'div':
                for p in sibling.find_all('p'):
                    content += p.get_text().strip() + " "

        cleaned = _clean_text(content)
        if len(cleaned) >= MIN_CHUNK_LEN:
            # Uzun EyeWiki bölümlerini de parçala
            _add_chunks(data, url, section_title, cleaned)

    return data


def scrape_optical_sites(urls: list) -> list:
    """
    Verilen URL listesini tarar.
    - Wikipedia için: h2/h3 başlıkları section adı olarak kullanılır.
    - EyeWiki ve diğerleri: h2/h3 → p kardeş yöntemi kullanılır.
    """
    all_data = []
    for url in urls:
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                print(f"  ⚠️  HTTP {response.status_code}: {url}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            if 'wikipedia.org' in url:
                chunks = _scrape_wikipedia(url, soup)
            else:
                chunks = _scrape_eyewiki(url, soup)

            if chunks:
                print(f"  ✅ {len(chunks):2d} chunk — {url}")
                all_data.extend(chunks)
            else:
                print(f"  ⚠️   0 chunk — {url} (içerik alınamadı)")

        except Exception as e:
            print(f"  ❌ Hata: {url} — {e}")

    return all_data