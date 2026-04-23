const express = require('express');
const axios = require('axios');
const router = express.Router();

router.post('/apply', async (req, res) => {
    try {
        const { userId, loanAmount, purpose, tenure, income, transactionHistory } = req.body;

        const pythonPayload = {
            userId: userId,
            loanAmount: loanAmount,
            purpose: purpose,
            tenure: tenure,
            income: income,
            existingDebt: 0, 
            accountCreatedAt: "2024-01-01", 
            transactionHistory: transactionHistory
        };

        console.log("Sending data to Python ML Engine...");
        // This calls your FastAPI server!
        const pythonResponse = await axios.post('http://localhost:8000/loan/predict-loan', pythonPayload);

        console.log(" Python ML Engine replied successfully!");
        res.status(200).json(pythonResponse.data);

    } catch (error) {
        console.error(" Error communicating with Python ML Service:", error.message);
        res.status(500).json({ error: "AI Service is currently unavailable" });
    }
});

module.exports = router;