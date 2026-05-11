from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI()

# load catalog
with open("catalog.json", "r", encoding="utf-8") as file:
    catalog = json.load(file)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.get("/")
def root():
    return {"message": "API Running"}


@app.get("/health")
def health():
    return {"status": "ok"}


def get_latest_user_message(messages):

    for msg in reversed(messages):

        if msg.role == "user":
            return msg.content.lower()

    return ""


def search_assessments(query):

    results = []

    for item in catalog:

        name = item.get("name", "").lower()

        if any(word in name for word in query.split()):

            results.append({
                "name": item["name"],
                "url": item["url"],
                "test_type": item.get("test_type", "General")
            })

    return results[:5]


@app.post("/chat")
def chat(data: ChatRequest):

    latest_message = get_latest_user_message(data.messages)

    if len(latest_message.split()) < 3:

        return {
            "reply": (
                "Please provide role, skills, or experience "
                "level for better recommendations."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    recommendations = search_assessments(latest_message)

    if not recommendations:

        return {
            "reply": (
                "No matching SHL assessments found."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    return {
        "reply": "Here are some recommended SHL assessments.",
        "recommendations": recommendations,
        "end_of_conversation": False
    }
