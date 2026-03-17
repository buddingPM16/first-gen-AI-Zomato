from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import sys
import os
import logging

# Path setup to import phase 4 logic
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from phase4_llm_integration.llm_recommender import generate_recommendation

app = FastAPI(
    title="Zomato AI Recommendation API",
    description="API to generate personalized Zomato restaurant recommendations using Groq and Llama 3.",
    version="1.0.0"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request and response validation
class RecommendationRequest(BaseModel):
    place: str = Field(..., description="The city or locality (e.g., 'Indiranagar')")
    cuisine: str = Field(..., description="The desired cuisine (e.g., 'Italian')")
    max_price: Optional[float] = Field(None, gt=0, description="Maximum budget for two people in INR")
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Minimum Zomato rating out of 5.0")
    top_n: int = Field(5, ge=1, le=10, description="Maximum number of restaurants to retrieve before sending to LLM")

class RecommendationResponse(BaseModel):
    recommendation: str

@app.post("/api/v1/recommend", response_model=RecommendationResponse)
def get_recommendation(req: RecommendationRequest):
    """
    Submits user preferences to the LLM Recommendation Engine and returns a tailored response.
    """
    try:
        logger.info(f"Received recommendation request: {req.dict()}")
        result = generate_recommendation(
            place=req.place,
            cuisine=req.cuisine,
            max_price=req.max_price,
            min_rating=req.min_rating,
            top_n=req.top_n
        )
        return RecommendationResponse(recommendation=result)
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Allows the script to be run directly for testing the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
