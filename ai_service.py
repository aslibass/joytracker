import google.generativeai as genai
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
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
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
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": JoyAnalysis
            }
        )
        return JoyAnalysis.model_validate_json(response.text)
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return None
