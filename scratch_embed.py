import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

for model_name in ["text-embedding-004", "models/text-embedding-004", "gemini-embedding-001", "models/gemini-embedding-2", "text-embedding-004"]:
    try:
        res = client.models.embed_content(model=model_name, contents="Hello")
        print(f"SUCCESS with {model_name}")
        print("type(res.embeddings):", type(res.embeddings))
        if res.embeddings:
            print("type(res.embeddings[0].values):", type(res.embeddings[0].values))
        break
    except Exception as e:
        print(f"FAILED with {model_name}: {e}")
