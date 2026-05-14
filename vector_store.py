import os
import time
import chromadb
import hashlib
from typing import Any
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
EMBED_MODEL = "gemini-embedding-001"

# Gemini ücretsiz katman: dakikada 100 istek limiti
# 0.7s bekleme → ~85 istek/dk (güvenli aralık)
RATE_LIMIT_DELAY = 0.7
MAX_RETRIES      = 5
RETRY_WAIT_BASE  = 35


def _embed_with_retry(text: str) -> list:
    """Embedding ister; 429 hatasında exponential backoff ile yeniden dener."""
    for attempt in range(MAX_RETRIES):
        try:
            result = client.models.embed_content(model=EMBED_MODEL, contents=text)
            if not result.embeddings or not result.embeddings[0].values:
                return []
            return list(result.embeddings[0].values)
        except Exception as e:
            if "429" in str(e):
                wait = RETRY_WAIT_BASE * (attempt + 1)
                print(f"  ⏳ Rate limit — {wait}s bekleniyor... (deneme {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                raise
    return []


def create_vector_db(scraped_data: list) -> None:
    chroma_client = chromadb.PersistentClient(path="./opti_db")
    collection    = chroma_client.get_or_create_collection(name="optirag_knowledge")

    total   = len(scraped_data)
    added   = 0
    skipped = 0
    print(f"🧠 {total} veri parçası vektörize ediliyor...")

    for i, entry in enumerate(scraped_data):
        doc_id = f"id_{i}"
        try:
            raw_id = f"{entry.get('url', '')}__{entry.get('section', str(i))}"
            doc_id = hashlib.md5(raw_id.encode()).hexdigest()

            # Mevcut kayıtları atla (yeniden ekleme önleme)
            existing = collection.get(ids=[doc_id])
            if existing and existing.get('ids'):
                skipped += 1
                continue

            time.sleep(RATE_LIMIT_DELAY)

            emb_values = _embed_with_retry(entry['text'])
            if not emb_values:
                print(f"  ❌ Embedding alınamadı — atlandı (id_{i})")
                skipped += 1
                continue

            collection.add(
                ids=[doc_id],
                embeddings=[emb_values],
                documents=[entry['text']],
                metadatas=[{
                    "source":  entry.get('url', ''),
                    "section": entry.get('section', 'Bilinmeyen Bölüm'),
                }],
            )
            added += 1

            if (i + 1) % 20 == 0:
                print(f"  📊 İlerleme: {i+1}/{total} — ✅{added} eklendi, ❌{skipped} atlandı")

        except Exception as e:
            print(f"  ❌ Beklenmeyen hata ({doc_id[:8]}...): {e}")
            skipped += 1

    print(f"\n✅ Vektör veritabanı tamamlandı: {added}/{total} chunk eklendi, {skipped} atlandı.")


def query_db(query_text: str, n_results: int = 5) -> Any:
    """
    Sorguya en yakın n_results dökümanı döndürür.
    n_results=5 (varsayılan) sayesinde daha kapsamlı bağlam sağlanır.
    """
    chroma_client = chromadb.PersistentClient(path="./opti_db")

    try:
        collection = chroma_client.get_collection(name="optirag_knowledge")
    except Exception:
        # Koleksiyon henüz oluşturulmamışsa boş sonuç döndür
        print("⚠️  optirag_knowledge koleksiyonu bulunamadı. 'python setup_db.py' çalıştırın.")
        return {"documents": [[]], "metadatas": [[]]}

    result = client.models.embed_content(model=EMBED_MODEL, contents=query_text)

    if not result.embeddings or not result.embeddings[0].values:
        return {"documents": [[]], "metadatas": [[]]}

    emb_values = list(result.embeddings[0].values)

    # Koleksiyondaki toplam belge sayısını al; istenen n_results'ı aşmamak için kırp
    count = collection.count()
    safe_n = min(n_results, count) if count > 0 else 1

    return collection.query(
        query_embeddings=[emb_values],
        n_results=safe_n,
        include=["documents", "metadatas", "distances"],
    )