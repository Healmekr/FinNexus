import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Force Python to read the .env file
load_dotenv()

# 2. Fetch the key
API_KEY = os.getenv("GEMINI_API_KEY")

# 3. DEBUG TRAP: This will print to your terminal so you can verify it worked
print("====================================")
print(f"DEBUG: Found API Key: {str(API_KEY)[:10]}... (hidden for security)")
print("====================================")

# 4. Configure Gemini
if not API_KEY:
    raise ValueError("API Key is completely missing. Check .env file!")
    
genai.configure(api_key=API_KEY)
llm_model = genai.GenerativeModel('gemini-2.5-flash-lite')


def generate_financial_advice(user_income, loan_amount, ml_decision, shap_reasons):
    prompt = f"""
    You are the FinNexus AI Financial Advisor. 
    A user earning ₹{user_income} applied for a ₹{loan_amount} loan.
    The ML model decision is: {'APPROVED' if ml_decision else 'REJECTED'}.
    The main factors were: {shap_reasons}.
    
    Give the user a short, professional, 3-step actionable plan based on this decision. 
    Do not use complex jargon. Be empathetic.
    """
    response = llm_model.generate_content(prompt)
    return response.text