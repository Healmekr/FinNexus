const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const auth = require('../middleware/auth');

// @route   POST /api/auth/signup
router.post('/signup', async (req, res) => {
  const { fullName, email, password, confirmPassword } = req.body;

  if (password !== confirmPassword) {
    return res.status(400).json({ msg: 'Passwords do not match' });
  }

  try {
    let user = await User.findOne({ email });
    if (user) return res.status(400).json({ msg: 'User already exists' });

    // Create new user with default financial data
    user = new User({
      fullName,
      email,
      password,
      balance: 49832,
      transactions: [
        { date: '2026-03-03', type: 'Transfer', amount: -2500, status: 'Success' },
        { date: '2026-03-02', type: 'Deposit', amount: 15000, status: 'Success' },
        { date: '2026-03-01', type: 'Transfer', amount: -800, status: 'Success' },
        { date: '2026-02-28', type: 'Loan EMI', amount: -5200, status: 'Success' },
        { date: '2026-02-27', type: 'Transfer', amount: -12000, status: 'Blocked' }
      ],
      spending: {
        Food: 12000,
        Transport: 9000,
        Shopping: 6000,
        Bills: 3000,
        Entertainment: 0
      },
      loanEligibility: 78
    });

    await user.save();

    const payload = { user: { id: user.id } };
    jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '7d' }, (err, token) => {
      if (err) throw err;
      res.json({ token, user: { id: user.id, fullName, email } });
    });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// @route   POST /api/auth/login
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await User.findOne({ email });
    if (!user) return res.status(400).json({ msg: 'Invalid credentials' });

    const isMatch = await user.matchPassword(password);
    if (!isMatch) return res.status(400).json({ msg: 'Invalid credentials' });

    const payload = { user: { id: user.id } };
    jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '7d' }, (err, token) => {
      if (err) throw err;
      res.json({ token, user: { id: user.id, fullName: user.fullName, email } });
    });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// @route   GET /api/auth/me
router.get('/me', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    res.json(user);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

module.exports = router;