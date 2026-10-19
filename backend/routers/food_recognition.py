from fastapi import (
    APIRouter, UploadFile, File, HTTPException, Form
)
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import base64
import json
import speech_recognition as sr
from pydub import AudioSegment
from PIL import Image
import io
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/api/food-recognition",
    tags=["Food Recognition"]
)

# --- CONFIG ---
# Initialize Groq Client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"


class NutritionInfo(BaseModel):
    calories: int
    protein: float
    carbs: float
    fats: float
    fiber: float
    sugar: float



# --- ROUTER ENDPOINT ---

@router.post("/analyze", response_model=FoodAnalysisResponse)
async def analyze(
    file: Optional[UploadFile] = File(None),
    text_context: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None)
):
    temp_files = []
    try:
        os.makedirs("temp_uploads", exist_ok=True)

        img_path = None
        if file:
            img_path = f"temp_uploads/{file.filename}"
            with open(img_path, "wb") as b:
                shutil.copyfileobj(file.file, b)
            temp_files.append(img_path)

        audio_text = ""
        if audio_file:
            audio_path = f"temp_uploads/{audio_file.filename}"
            with open(audio_path, "wb") as b:
                shutil.copyfileobj(audio_file.file, b)
            temp_files.append(audio_path)
            audio_text = transcribe_audio(audio_path)

        full_context = f"{text_context or ''} {audio_text}".strip()

        if not img_path and not full_context:
            raise HTTPException(
                status_code=400,
                detail="No input provided"
            )

        llm_response = analyze_with_groq(img_path, full_context)

        data = {}
        if llm_response == "ERROR":
            data = {
                # Remaining code is below the visible area
            }
