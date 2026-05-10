
import requests
from bs4 import BeautifulSoup

def scrape_optical_sites(urls):
    all_data = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            for header in soup.find_all(['h1', 'h2', 'h3']):
                section_title = header.get_text().strip()
                content = ""
                for sibling in header.find_next_siblings():
                    if sibling.name in ['h1', 'h2', 'h3']: break
                    if sibling.name == 'p':
                        content += sibling.get_text().strip() + " "
                if len(content) > 100:
                    all_data.append({"url": url, "section": section_title, "text": content})
        except Exception as e:
            print(f"Hata: {url} taranamadı. {e}")
    return all_data
