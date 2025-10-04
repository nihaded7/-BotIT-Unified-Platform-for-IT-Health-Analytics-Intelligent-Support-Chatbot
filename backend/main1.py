from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from .processing import process_data
import json

app = FastAPI()

# Allow frontend to connect (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change "*" to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend is running!"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    cleaning_options: str = Form(...)
):
    """
    Upload a CSV + cleaning options (as JSON string).
    Example cleaning_options: {"drop_na": true, "fill_na": "mean", "remove_duplicates": true}
    """
    # Read file into DataFrame
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {e}")

    # Parse cleaning options JSON string → Python dict
    try:
        options = json.loads(cleaning_options)
        if not isinstance(options, dict):
            raise ValueError("cleaning_options must be a JSON object")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid cleaning_options: {e}")

    # Process data
    try:
        results = process_data(df, options)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return results
