import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import shutil
import uuid
import json
import base64
import time
from datetime import datetime
from contextlib import asynccontextmanager

from auditor import analyze_image_with_gemini, init_gemini
from azure_auditor import analyze_image_with_azure, init_azure
from visualizer import create_heatmap_overlay

AUDIT_DB_PATH = "database.json"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load or initialize DB
    if not os.path.exists(AUDIT_DB_PATH):
        with open(AUDIT_DB_PATH, "w") as f:
            json.dump([], f)
            
    # Initialize LLM Provider
    provider = os.environ.get("LLM_PROVIDER", "GEMINI").upper()
    print(f"Initializing LLM Provider: {provider}")
    
    if provider == "AZURE":
        init_azure()
    else:
        init_gemini()
    
    yield
    # Cleanup if needed

app = FastAPI(lifespan=lifespan)

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production (Hackathon safe)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (uploaded images, heatmaps) if necessary for local dev
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

class AuditUpdate(BaseModel):
    audit_id: str
    items: List[dict] # Simplified for now, will refine

def save_audit(new_audit):
    """Helper to save audit to JSON DB"""
    if not os.path.exists(AUDIT_DB_PATH):
        with open(AUDIT_DB_PATH, "w") as f:
            json.dump([], f)
            
    with open(AUDIT_DB_PATH, "r+") as f:
        try:
            db = json.load(f)
        except json.JSONDecodeError:
            db = []
            
        db.append(new_audit)
        f.seek(0)
        json.dump(db, f, indent=2)
        f.truncate()

@app.get("/")
def read_root():
    return {"message": "Sustainable Energy Auditor API is running"}

@app.post("/audit")
async def create_audit(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        filename = f"uploads/{file.filename}"
        with open(filename, "wb") as f:
            f.write(contents)
        
        # Calculate Hash for Caching
        import hashlib
        file_hash = hashlib.sha256(contents).hexdigest()
        
        # Check Cache in DB
        if os.path.exists(AUDIT_DB_PATH):
            with open(AUDIT_DB_PATH, "r") as f:
                try:
                    db = json.load(f)
                    for record in db:
                        # Check if hash matches (if we stored it) or if filename matches (simple fallback)
                        # Ideally we store hash. For now, let's check if we can match content.
                        # Since we didn't store hash before, we'll start storing it. 
                        # Only return cached if explicitly checking hash or if filename + size matches?
                        # Let's trust hash.
                        if record.get("image_hash") == file_hash:
                            print(f"[⚡] CACHE HIT! Returning existing analysis for {filename}")
                            return record
                except:
                    pass

        start_time = time.time()
        print(f"\n--- [START] Analysis Request for {filename} ---")
        
        # 1. Analyze with LLM
        print(f"[1/3] 🧠 Sending image to AI Model ({os.environ.get('LLM_PROVIDER', 'GEMINI')})...")
        print("      (This typically takes 5-10 seconds depending on API load)")
        
        provider = os.environ.get("LLM_PROVIDER", "GEMINI").upper()
        if provider == "AZURE":
            analysis_result = await analyze_image_with_azure(contents)
        else:
            analysis_result = await analyze_image_with_gemini(contents)
            
        llm_time = time.time() - start_time
        print(f"[✔] AI Analysis Complete in {llm_time:.2f}s")
        
        # 2. Generate Heatmap
        print("[2/3] 🔥 Generating Thermal Heatmap...")
        # Support both 'opportunities' (new) and 'detections' (old)
        items_to_visualize = analysis_result.get("opportunities", [])
        if not items_to_visualize:
            items_to_visualize = analysis_result.get("detections", [])
            
        heatmap_path = create_heatmap_overlay(filename, items_to_visualize)
        
        # Add heatmap path to result
        analysis_result["heatmap_path"] = heatmap_path
        print(f"[✔] Heatmap saved to {heatmap_path}")
        
        # 3. Save to DB
        print("[3/3] 💾 Saving to Database...")
        new_audit = {
            "id": str(uuid.uuid4())[:8],
            "original_image": filename,
            "image_hash": file_hash, # Store hash for future cache hits
            "heatmap_image": heatmap_path,
            "analysis": analysis_result,
            "timestamp": datetime.now().strftime("%Y-%m-%d")
        }
        
        save_audit(new_audit)
        
        total_time = time.time() - start_time
        print(f"--- [DONE] Total Process Time: {total_time:.2f}s ---\n")
        
        return new_audit
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    with open(AUDIT_DB_PATH, "r") as f:
        return json.load(f)
