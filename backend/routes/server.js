const express = require('express');
const cors = require('cors');
const loanRoutes = require('./loanRoutes');

const app = express();
app.use(cors());
app.use(express.json());

// Tell Node to use the routes we just created
app.use('/api/loan', loanRoutes);

const PORT = 5000;
app.listen(PORT, () => {
    console.log(` Node.js Backend running on http://localhost:${PORT}`);
});