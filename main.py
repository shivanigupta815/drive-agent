from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import chat

app = FastAPI(title="Drive Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list = []   # [{"role": "user"/"assistant", "content": "..."}]


@app.get("/")
def root():
    return {"status": "Drive Agent is running!"}


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        print("Received message:", request.message)

        response = chat(request.message, request.history)

        print("Response:", response)

        return {"response": response}

    except Exception as e:
        import traceback

        print("ERROR OCCURRED:")
        traceback.print_exc()

        return {"error": str(e)}