from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

app = FastAPI()

# load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# load saved catalog
with open("catalog.json", "r", encoding="utf-8") as file:
    catalog = json.load(file)

# load vector index
index = faiss.read_index("shl_index.bin")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.get("/health")
def health():
    return {"status": "ok"}


def get_latest_user_message(messages):
    for msg in reversed(messages):
        if msg.role == "user":
            return msg.content
    return ""


def query_is_vague(text):
    vague_words = [
        "assessment",
        "test",
        "hire someone",
        "need hiring test"
    ]

    text = text.lower()

    for word in vague_words:
        if word in text:
            return True

    return False


def search_assessments(user_query, top_k=5):

    query_vector = model.encode([user_query])

    distances, indexes = index.search(
        np.array(query_vector),
        top_k
    )

    results = []

    for idx in indexes[0]:

        if idx < len(catalog):

            item = catalog[idx]

            results.append({
                "name": item["name"],
                "url": item["link"],
                "test_type": item.get("test_type", "General")
            })

    return results


@app.post("/chat")
def chat(data: ChatRequest):

    latest_message = get_latest_user_message(data.messages)

    # clarification handling
    if query_is_vague(latest_message):

        return {
            "reply": (
                "Can you tell me the role, "
                "experience level, or important skills "
                "for the candidate?"
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    # comparison handling
    if "difference" in latest_message.lower():

        return {
            "reply": (
                "OPQ mainly measures personality and "
                "behavior at work, while GSA focuses "
                "more on cognitive and reasoning ability."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    # off-topic handling
    blocked_topics = [
        "legal advice",
        "politics",
        "medical"
    ]

    for topic in blocked_topics:
        if topic in latest_message.lower():

            return {
                "reply": (
                    "I can only help with SHL assessment "
                    "recommendations."
                ),
                "recommendations": [],
                "end_of_conversation": True
            }

    recommendations = search_assessments(latest_message)

    return {
        "reply": "These assessments may fit your requirements.",
        "recommendations": recommendations,
        "end_of_conversation": False
    }