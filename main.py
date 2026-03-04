import time
import json
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import redis
from transformers import pipeline

from database import engine, Base, get_db
from models import PredictionLog
from schemas import PredictionRequest, PredictionResponse

# Initialize DB (only if running as main or in non-test environment)
if os.getenv("TESTING") != "True":
    # Simple retry logic for DB connection
    for i in range(5):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception as e:
            print(f"Database connection attempt {i+1} failed: {e}")
            time.sleep(3)

# Load environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")
CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))

app = FastAPI(title="AI Inference Cache Gateway")

# Initialize Redis
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_client = None

# Initialize ML Model (Mocked for now if transformers fails to load or for speed)
try:
    classifier = pipeline("sentiment-analysis", model=MODEL_NAME)
except Exception as e:
    print(f"Model loading failed: {e}. Using mock inference.")
    classifier = None

def mock_inference(text: str):
    # Very simple mock: positive if text is long, negative otherwise
    score = min(0.99, 0.5 + len(text) / 1000)
    label = "POSITIVE" if len(text) > 10 else "NEGATIVE"
    return [{"label": label, "score": score}]

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    text = request.text
    
    # 1. Check Redis Cache
    if redis_client:
        cached_result = redis_client.get(text)
        if cached_result:
            result = json.loads(cached_result)
            latency = time.time() - start_time
            
            # Log to DB (Cache Hit)
            log_entry = PredictionLog(
                input_text=text,
                output_label=result['label'],
                score=result['score'],
                latency=latency,
                cache_hit=1
            )
            db.add(log_entry)
            db.commit()
            
            return PredictionResponse(
                text=text,
                label=result['label'],
                score=result['score'],
                latency=latency,
                cached=True,
                timestamp=datetime.utcnow()
            )

    # 2. Run Inference
    inference_start = time.time()
    if classifier:
        inference_result = classifier(text)[0]
    else:
        inference_result = mock_inference(text)[0]
    
    result = {
        "label": inference_result["label"],
        "score": inference_result["score"]
    }
    
    # 3. Cache in Redis
    if redis_client:
        redis_client.setex(text, CACHE_TTL, json.dumps(result))

    latency = time.time() - start_time
    
    # 4. Log to DB (Cache Miss)
    log_entry = PredictionLog(
        input_text=text,
        output_label=result['label'],
        score=result['score'],
        latency=latency,
        cache_hit=0
    )
    db.add(log_entry)
    db.commit()

    return PredictionResponse(
        text=text,
        label=result['label'],
        score=result['score'],
        latency=latency,
        cached=False,
        timestamp=datetime.utcnow()
    )

@app.get("/health")
async def health():
    return {"status": "ok", "redis": redis_client is not None, "model": classifier is not None}
