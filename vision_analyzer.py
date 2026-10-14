import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
import PIL.Image
from prompts import SYSTEM_PROMPT, JSON_SCHEMA

# Load environment variables from .env
load_dotenv()

def analyze_screenshot(image_path: str) -> dict:
    """
    Analyzes a UI screenshot and returns structured JSON about any visual issues.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the .env file. Please create a .env file based on .env.example.")

    # Initialize the GenAI client
    client = genai.Client(api_key=api_key)
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    # Use gemini-2.5-flash which is excellent for multimodal tasks
    model_name = "gemini-2.5-flash"
    
    # Load the image using PIL
    image = PIL.Image.open(image_path)
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[SYSTEM_PROMPT, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JSON_SCHEMA,
                temperature=0.1, # Low temperature for more deterministic, analytical responses
            ),
        )
        
        # Parse the JSON response
        result_json = json.loads(response.text)
        return result_json
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return {
            "issue_detected": False,
            "element": "error",
            "issue_type": "error",
            "severity": "high",
            "description": f"Failed to analyze image: {str(e)}",
            "suggested_fix": ""
        }

if __name__ == "__main__":
    print("Vision Analyzer module loaded successfully.")
    print("Run test_vision.py to execute the module with sample images.")
