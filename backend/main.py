from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
from pathlib import Path

from backend.rag import chat_engine
from backend.services import metrics_service

app = FastAPI(title="Language Academy Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Initializing server...")
    try:
        chat_engine.load_documents()
    except Exception as e:
        print(f"Failed to load documents on startup: {e}")

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    if not req.message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    reply = chat_engine.ask(req.message)
    return {"reply": reply}

@app.get("/api/metrics")
async def metrics_endpoint():
    return metrics_service.get_metrics()

@app.get("/api/config")
async def config_endpoint():
    return {
        "escalation_form_url": os.getenv("ESCALATION_FORM_URL", "https://docs.google.com/forms/d/e/1FAIpQLSdAyhhqdotfhe9bwKaCC0faNaArmJLSjQOmuD9feRl0pEd95A/viewform")
    }

# Serve static frontend (if built)
# Only map if directory exists (for production)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "dist"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    @app.get("/")
    def root_fallback():
        return {"message": "Backend API is running. Frontend build not found."}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=3000, reload=True)
