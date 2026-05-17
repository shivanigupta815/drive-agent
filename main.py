from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent import chat

app = FastAPI(
    title="Drive Agent API",
    description="Google Drive AI Assistant API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list = []  # [{"role": "user"/"assistant", "content": "..."}]


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "Drive Agent is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """Health check for load balancers"""
    return {"status": "healthy"}


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """Chat endpoint for Drive file search"""
    try:
        response = chat(request.message, request.history)
        return {"response": response, "success": True}

    except ValueError as e:
        return {
            "error": "Configuration error",
            "success": False
        }
    except Exception as e:
        return {
            "error": "An error occurred while processing your request",
            "success": False
        }