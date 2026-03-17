import os
import sys
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from groq import Groq

# Add previous phase to path to reuse the DB query function
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from phase3_indexing_storage.database_manager import query_restaurants

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables (like GROQ_API_KEY)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Ensure API key exists
if not os.environ.get("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY environment variable not set. Please create a .env file with your key.")

# Initialize the Groq Client
client = Groq()

def generate_recommendation(place: str, cuisine: str, max_price: Optional[float] = None, min_rating: Optional[float] = None, top_n: int = 5) -> str:
    """
    1. Queries the local SQLite database for matching restaurants.
    2. Constructs a prompt with the context.
    3. Calls the Groq LLM (Llama 3) to generate a helpful, conversational response.
    """
    price_str = f" under ₹{max_price}" if max_price is not None else ""
    rating_str = f" with {min_rating}+ rating" if min_rating is not None else ""
    
    logger.info(f"Querying database for {cuisine} in {place}{price_str}{rating_str}...")
    restaurants = query_restaurants(place, cuisine, max_price, min_rating, top_n)
    
    if not restaurants:
        return f"I'm sorry, I couldn't find any {cuisine} restaurants in {place}{price_str}{rating_str}. Try adjusting your preferences!"

    # Format the context strictly for the LLM
    context_lines = []
    for i, r in enumerate(restaurants):
        context_lines.append(f"{i+1}. {r['name']} ({r['location']}) - Rating: {r['rating']} - Cost for two: ₹{r['cost_for_two']} - Cuisines: {r['cuisines']} - Zomato Link: {r['url']}")
    
    context_str = "\n".join(context_lines)
    logger.info(f"Found {len(restaurants)} matching restaurants. Sending to Groq LLM...")
    
    # Construct the System and User Prompt
    system_prompt = (
        "You are an expert, local food critic and restaurant recommender in India. "
        "Your goal is to provide clear, friendly, and structured restaurant recommendations based ONLY on the data provided. "
        "Explain *why* each place is a good fit based on the user's constraints, using an engaging and highly scannable tone (e.g., bullet points and bold text). "
        "CRITICAL: For every restaurant you recommend, you MUST include its Zomato Link as a clickable markdown hyperlink formatted like this: [View on Zomato](URL)."
    )
    
    user_prompt = f"A user is looking for {cuisine} food in {place}. "
    if max_price is not None:
        user_prompt += f"They want to spend under ₹{max_price} for two people, "
    if min_rating is not None:
        user_prompt += f"and want a place with a rating of at least {min_rating} stars. "
    user_prompt += "\n\n"
    
    user_prompt += (
        f"Based on their preferences, here are the top matching restaurants we found in our database:\n{context_str}\n\n"
        "Please provide a final recommendation to the user summarizing their best options from this list."
    )
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1024
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    test_place = "Indiranagar"
    test_cuisine = "italian"
    test_price = 2000.0
    test_rating = 4.5
    
    print("="*50)
    print(f"Testing Recommendation Engine for: {test_cuisine} in {test_place}")
    print("="*50)
    
    recommendation = generate_recommendation(
        place=test_place,
        cuisine=test_cuisine,
        max_price=test_price,
        min_rating=test_rating
    )
    
    print("\n[LLM RESPONSE]:\n")
    print(recommendation)
