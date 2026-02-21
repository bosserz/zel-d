import json
import os
import numpy as np
from openai import OpenAI

EMBED_MODEL = "text-embedding-3-large"

def load_kb_texts(products_path="data/products.json", faq_path="data/faq.md"):
    texts = []

    #products
    with open(products_path, "r", encoding="utf-8") as f:
        products = json.load(f)
        for p in products:
            facts = ", ".join([f"{k}: {v}" for k, v in p.get("key_facts", {}).items()])
            text = (
                f"TYPE: product\n"
                f"SKU: {p.get('sku')}\n"
                f"Name: {p.get('name')}\n"
                f"Category: {p.get('category')}\n"
                f"Description: {p.get('description')}\n"
                f"Key Facts: {facts}"
            )
            texts.append(text)

    with open(faq_path, "r", encoding="utf-8") as f:
        faq = f.read().strip()
    
    chunks = [c.strip() for c in faq.split("\n\n") if c.strip()]
    for c in chunks:
        texts.append(f"TYPE: policy_or_faq\n{c}")

    return texts

def embed_texts(client: OpenAI, texts):
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vectors = np.array([d.embedding for d in resp.data], dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
    return vectors / norms

def build_or_load_index(client: OpenAI, cache_path:"data/embeddings_cache.npz"):
    texts = load_kb_texts()

    if os.path.exists(cache_path):
        data = np.load(cache_path, allow_pickle=True)
        cached_texts = data["texts"].tolist()
        vectors = data["vectors"]
        if cached_texts == texts:
            return texts, vectors
        
    vectors = embed_texts(client, texts)
    np.savez(cache_path, texts=np.array(texts, dtype=object), vectors=vectors)
    return texts, vectors

def retrieve_top_k(client: OpenAI, query: str, k=4, cache_path="data/embeddings_cache.npz"):
    texts, vectors = build_or_load_index(client, cache_path)
    query_vec = embed_texts(client, [query])[0]
    sims = np.dot(vectors, query_vec)
    top_k_idx = np.argsort(sims)[-k:][::-1]
    return [(texts[i], float(sims[i])) for i in top_k_idx]