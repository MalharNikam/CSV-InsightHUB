import os
import logging
import pandas as pd
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

from app.utils.auth_token import get_current_user
from app.models.user import User

# ─── 1) Load .env & Setup Logging ─────────────────────────────
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()

# ─── 2) List Uploaded CSVs ────────────────────────────────────
@router.get("/files")
async def list_user_files(current_user: User = Depends(get_current_user)):
    user_dir = os.path.join("uploads", current_user.email.replace("@", "_"))
    if not os.path.isdir(user_dir):
        return {"files": []}
    files = sorted(
        [f for f in os.listdir(user_dir) if f.lower().endswith(".csv")],
        reverse=True,
    )
    return {"files": files[:5]}  # Show only last 5 files


# ─── 3) Request Schema ────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str


# ─── 4) Chat Endpoint ─────────────────────────────────────────
@router.post("/chat")
async def chat_with_bot(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    # A) Locate Latest CSV
    user_dir = os.path.join("uploads", current_user.email.replace("@", "_"))
    if not os.path.isdir(user_dir):
        raise HTTPException(404, "Please upload your CSV first.")

    csvs = sorted(
        [f for f in os.listdir(user_dir) if f.lower().endswith(".csv")],
        reverse=True,
    )

    if not csvs:
        raise HTTPException(404, "No CSV files found.")

    csv_path = os.path.join(user_dir, csvs[0])
    if not os.path.exists(csv_path):
        raise HTTPException(404, "CSV file not found. It may have been deleted.")

    # B) Load DataFrame
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        raise HTTPException(400, "Couldn't read CSV. Is it valid?")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    max_rows = int(os.getenv("MAX_DF_ROWS", "10000"))
    if len(df) > max_rows:
        df = df.head(max_rows)

    # C) Init Google Gemini
    google_key = os.getenv("GOOGLE_API_KEY")
    if not google_key:
        raise HTTPException(500, "Missing GOOGLE_API_KEY in .env")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.7,
        google_api_key=google_key,
    )

    # D) Prepare LLMChain
    prompt = PromptTemplate(
        input_variables=["question", "dataframe"],
        template="""
You are an expert in employee data analysis. Please answer the following question based on the provided employee dataset.

Dataset:
{dataframe}

Question:
{question}

Answer:
"""
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    # E) Pass CSV and Question
    try:
        reply = await chain.arun({
            "question": request.message,
            "dataframe": df.head(30).to_string()  # send top 30 rows
        })
    except Exception as e:
        logger.error(f"LLMChain error: {e}")
        raise HTTPException(500, f"Error processing your query: {e}")

    return {"response": reply}
