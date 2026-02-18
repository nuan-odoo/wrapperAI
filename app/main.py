from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Optional, List
from app.browser_manager import BrowserManager
from app.config import CHATBOT_CONFIGS

browser_manager = BrowserManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # Browser starts only after /setup is called, not on boot
    await browser_manager.stop()


app = FastAPI(
    title="WrapperAI",
    description="A shadow/wrapper API that drives a chatbot GUI. Built for educational purposes.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the setup GUI
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --- Request / Response models ---

class SetupRequest(BaseModel):
    target: str
    cookies: Optional[List[dict]] = None  # For Claude
    email: Optional[str] = None           # For ChatGPT / Gemini
    password: Optional[str] = None        # For ChatGPT / Gemini

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    response: str
    bot: str


# --- Endpoints ---

@app.get("/", include_in_schema=False)
async def root():
    """Serve the setup GUI on first visit."""
    return FileResponse("app/static/index.html")


@app.post("/setup")
async def setup(request: SetupRequest):
    """
    Called by the setup GUI to initialise the browser session.
    Accepts either cookies (Claude) or email+password (ChatGPT/Gemini).
    """
    if request.target not in CHATBOT_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Unknown target '{request.target}'. Choose from: {list(CHATBOT_CONFIGS.keys())}")

    if browser_manager.is_ready:
        raise HTTPException(status_code=400, detail="Session already active. Restart the container to reconfigure.")

    try:
        await browser_manager.start(
            target=request.target,
            cookies=request.cookies,
            email=request.email,
            password=request.password,
        )
        return {"status": "ok", "bot": request.target}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start browser: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the active chatbot and return the response.
    Requires /setup to have been completed first.
    """
    if not browser_manager.is_ready:
        raise HTTPException(status_code=503, detail="Not configured yet. Visit http://localhost:8000 to complete setup.")

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        response = await browser_manager.send_message(request.message)
        return ChatResponse(
            message=request.message,
            response=response,
            bot=browser_manager.active_bot
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Browser automation error: {str(e)}")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "configured": browser_manager.is_ready,
        "active_bot": browser_manager.active_bot,
    }
