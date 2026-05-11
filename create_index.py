import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# load catalog
with open("catalog.json", "r", encoding="utf-8") as file:
    catalog = json.load(file)

# prepare text for embeddings
texts = []

for item in catalog:

    text = f"""
    Name: {item['name']}
    Type: {item.get('test_type', '')}
    """

    texts.append(text)

# generate embeddings
embeddings = model.encode(texts)

# create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings).astype("float32"))

# save index
faiss.write_index(index, "shl_index.bin")

print("FAISS index created successfully")