from google import genai
from google.genai import types
from database import settings
import json
from typing import List, Optional
from pydantic import BaseModel

# Define the response schema for structured output
class JoyAnalysis(BaseModel):
    category: str # Faith, Family, Provision, Health, Nature, Work, Other
    sentiment_score: int # 1-10
    is_urgent: bool
    tags: List[str]
    pastor_summary: str

def analyze_joy_entry(content: str) -> Optional[JoyAnalysis]:
    client = genai.Client(api_key=settings.gemini_api_key)
    
    prompt = f"""
    Analyze the following joy entry for a church community app.
    
    Entry: "{content}"
    
    Return a JSON object with:
    - category: Choose one from (Faith, Family, Provision, Health, Nature, Work, Other)
    - sentiment_score: 1 to 10 rating of joy/gratitude.
    - is_urgent: Boolean. True ONLY if the entry indicates a crisis, self-harm, abuse, or urgent pastoral need.
    - tags: A list of 2-3 relevant keywords.
    - pastor_summary: A 1-sentence summary for a church leader.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=JoyAnalysis,
            ),
        )
        return response.parsed
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        import traceback
        traceback.print_exc()
        return None
