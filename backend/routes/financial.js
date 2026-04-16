const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const User = require('../models/User');

router.get('/me', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('balance transactions spending loanEligibility');
    res.json(user);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

router.post('/transfer', auth, async (req, res) => {
  const { recipient, amount } = req.body;
  if (!recipient || !amount || amount <= 0) {
    return res.status(400).json({ msg: 'Invalid recipient or amount' });
  }

  try {
    const user = await User.findById(req.user.id);
    if (!user) return res.status(404).json({ msg: 'User not found' });

    if (amount > user.balance) {
      return res.status(400).json({ msg: 'Insufficient balance' });
    }

    user.balance -= amount;

    const newTransaction = {
      date: new Date().toISOString().slice(0,10),
      type: `Transfer to ${recipient}`,
      amount: -amount,
      status: 'Success'
    };
    user.transactions.unshift(newTransaction);
    if (user.transactions.length > 10) user.transactions.pop();

    await user.save();

    res.json({
      success: true,
      newBalance: user.balance,
      transaction: newTransaction
    });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

router.post('/add-funds', auth, async (req, res) => {
  const { amount } = req.body;
  if (!amount || amount <= 0) {
    return res.status(400).json({ msg: 'Invalid amount' });
  }

  try {
    const user = await User.findById(req.user.id);
    if (!user) return res.status(404).json({ msg: 'User not found' });

    user.balance += amount;

    const newTransaction = {
      date: new Date().toISOString().slice(0,10),
      type: 'Cash Deposit',
      amount: amount,
      status: 'Success'
    };
    user.transactions.unshift(newTransaction);
    if (user.transactions.length > 10) user.transactions.pop();

    await user.save();

    res.json({
      success: true,
      newBalance: user.balance,
      transaction: newTransaction
    });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

router.post('/dynamic-update', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    if (!user) return res.status(404).json({ msg: 'User not found' });

    const change = Math.floor(Math.random() * 201) - 100;
    user.balance = Math.max(0, user.balance + change);

    const newTransaction = {
      date: new Date().toISOString().slice(0,10),
      type: change > 0 ? 'Deposit' : 'Transfer',
      amount: change,
      status: Math.random() > 0.9 ? 'Blocked' : 'Success'
    };
    user.transactions.unshift(newTransaction);
    if (user.transactions.length > 10) user.transactions.pop();

    const categories = Object.keys(user.spending.toObject());
    if (categories.length) {
      const randomCat = categories[Math.floor(Math.random() * categories.length)];
      const newValue = Math.max(0, (user.spending[randomCat] || 0) + Math.floor(change * 0.2));
      user.spending[randomCat] = newValue;
    }

    await user.save();
    res.json({ balance: user.balance, transactions: user.transactions, spending: user.spending });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

module.exports = router;