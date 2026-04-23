from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np

# Your Gemini AI Advisor function (assuming it's in app/models/advisor.py)
from app.models.advisor import generate_financial_advice

app = FastAPI(title="FinNexus AI Service", version="1.0.0")

# Enable CORS for Node.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:3000"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 1. DEFINE THE DATA STRUCTURES (Pydantic)
# These MUST match the JSON sent from Node.js/Thunder Client exactly
# ==========================================
class LoanRequest(BaseModel):
    monthly_income: float
    loan_amount: float
    loan_tenure: int
    loan_purpose: str
    avg_monthly_savings: float
    savings_rate: float
    savings_consistency: float
    avg_monthly_spending: float
    spending_volatility: float
    transaction_count: int
    avg_transaction_size: float
    debt_to_income_ratio: float
    account_age_months: int

class FraudRequest(BaseModel):
    amount: float
    hour: int
    daily_tx_count: int
    is_new_recipient: int
    amount_variance_ratio: float
    is_round_amount: int

# ==========================================
# 2. ENDPOINTS
# ==========================================
@app.get("/")
def root():
    return {"message": "FinNexus AI Engine Running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# --- LOAN PREDICTION ENDPOINT ---
@app.post("/predict-loan")
async def predict_loan(req: LoanRequest):
    try:
        # In the future, this is where you will load loan_classifier.pkl
        # and pass these features into model.predict()
        
        # For now, we simulate the ML math working successfully
        ml_decision = True if req.debt_to_income_ratio < 0.4 else False
        confidence = 0.85 if ml_decision else 0.72
        shap_reasons = "Debt-to-income ratio is healthy and savings rate is consistent."

        # Pass the data to Gemini for the human explanation
        advice = generate_financial_advice(
            user_income=req.monthly_income, 
            loan_amount=req.loan_amount, 
            ml_decision=ml_decision, 
            shap_reasons=shap_reasons
        )

        return {
            "status": "success",
            "approved": ml_decision,
            "confidence": confidence,
            "ai_advisor_message": advice
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- FRAUD DETECTION ENDPOINT ---
@app.post("/analyze-fraud")
async def analyze_fraud(req: FraudRequest):
    try:
        # In the future, this is where you will load fraud_detector.pkl
        # and pass these features into model.predict()

        # Simulated Fraud Logic based on the test data
        is_fraud = True if req.amount_variance_ratio > 10.0 or req.daily_tx_count > 15 else False
        risk_level = "HIGH" if is_fraud else "LOW"
        
        reasons = []
        if req.amount_variance_ratio > 10.0:
            reasons.append(f"Amount is {req.amount_variance_ratio}x higher than user's average.")
        if req.is_new_recipient == 1:
            reasons.append("First time sending to this recipient.")

        return {
            "status": "success",
            "riskLevel": risk_level,
            "shouldBlock": is_fraud,
            "reasons": reasons
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))