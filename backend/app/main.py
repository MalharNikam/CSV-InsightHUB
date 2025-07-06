from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app.models import user  # ensures User model is registered
from app.routes import auth, upload, chat

# ─── 1) Load environment variables ───────────────────────────────────
load_dotenv()  # Make sure .env is read before any config

# ─── 2) Create FastAPI app ───────────────────────────────────────────
app = FastAPI(title="Employee Insights API")

# ─── 3) Enable CORS for your frontend (e.g., Streamlit) ──────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Replace ["*"] with your frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 4) Create database tables ────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── 5) Root endpoint ─────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"message": "Employee Insights API is live!"}

# ─── 6) Include route modules ─────────────────────────────────────────
app.include_router(auth.router,   prefix="/auth",   tags=["auth"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(chat.router,   prefix="/chat",   tags=["chat"])