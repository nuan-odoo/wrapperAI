from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from app.browser_manager import BrowserManager

# One shared browser session for all requests
browser_manager = BrowserManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the browser when the server boots up
    await browser_manager.start()
    yield
    # Shut the browser down cleanly when the server stops
    await browser_manager.stop()


app = FastAPI(
    title="WrapperAI",
    description="A shadow/wrapper API that drives a chatbot GUI. Built for educational purposes.",
    version="1.0.0",
    lifespan=lifespan
)

# Allow requests from any origin (fine for a uni project)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request / Response shapes ---

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    response: str


# --- Endpoints ---

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get a response back — just like a real LLM API.
    
    Example request body:
    {
        "message": "What is a wrapper API?"
    }
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        response = await browser_manager.send_message(request.message)
        return ChatResponse(message=request.message, response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Browser automation error: {str(e)}")


@app.get("/health")
async def health():
    """Check that the API and browser session are alive."""
    return {
        "status": "ok",
        "browser_active": browser_manager.page is not None
    }


@app.get("/")
async def root():
    """Landing page — points to the interactive docs."""
    return {
        "name": "WrapperAI",
        "docs": "/docs",
        "health": "/health",
        "chat": "/chat"
    }
