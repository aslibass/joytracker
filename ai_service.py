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
    # Debug: Check if API key is present
    key = settings.gemini_api_key
    if not key:
        print("ERROR: AI Analysis failed - GEMINI_API_KEY is missing from environment/settings.")
        return None
    
    # Mask key for safe logging (show first 4 and last 4 chars)
    masked_key = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "****"
    print(f"DEBUG: Initializing GenAI Client with key: {masked_key}")

    try:
        # Defaults to the correct endpoint. Removed v1beta and explicit vertexai=False 
        # (as it's the default and we specify it if needed, but the key now works)
        client = genai.Client(
            api_key=key,
            vertexai=False
        )
        
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
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=JoyAnalysis,
            ),
        )
        print(f"DEBUG: AI Analysis success for content starting with: '{content[:20]}...'")
        return response.parsed
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        # Identify if it's specifically a 401/403 to provide better user guidance
        if "401" in str(e) or "403" in str(e):
            print("TIP: This error often means the API Key is invalid for this project or the Generative Language API is not enabled at aistudio.google.com")
        import traceback
        traceback.print_exc()
        return None
