import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load the key from your .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

print("====================================")
print("📡 QUERYING GOOGLE SERVERS...")
print("====================================")

try:
    # Ask Google for the list of models that support text generation
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            print(f"✅ Found Supported Model: {m.name}")
    
    if not available_models:
        print("❌ No text generation models found for this API key/region.")
        
except Exception as e:
    print(f"❌ ERROR: {e}")