from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.main1 import app as analysis_app
from backend.chatboot.main import app as chatbot_app

app = FastAPI(title="Unified IT Support System", version="2.0.0")

# One CORS config for everything
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount both apps
app.mount("/analysis", analysis_app)  # gives /analysis/upload
app.mount("/", chatbot_app)           # keeps /chat, /start-session, /session/{id} as-is

# Optional: top-level health and session management
@app.get("/")
def health():
    return {
        "status": "ok", 
        "version": "2.0.0",
        "services": {
            "analysis": "/analysis",
            "chatbot": "/",
            "session_management": "/start-session, /session/{id}"
        }
    }

@app.get("/health")
def detailed_health():
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "features": [
            "Data Analysis & Problem Detection",
            "Smart IT Support Chatbot",
            "Conversation Memory & Context",
            "Hybrid Database + AI Responses"
        ]
    }


