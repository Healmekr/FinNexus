const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const transactionSchema = new mongoose.Schema({
  date: { type: String, required: true },
  type: { type: String, required: true },
  amount: { type: Number, required: true },
  status: { type: String, default: 'Success' }
});

const spendingSchema = new mongoose.Schema({
  Food: { type: Number, default: 0 },
  Transport: { type: Number, default: 0 },
  Shopping: { type: Number, default: 0 },
  Bills: { type: Number, default: 0 },
  Entertainment: { type: Number, default: 0 }
});

const UserSchema = new mongoose.Schema({
  fullName: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
  // Financial data (per user)
  balance: { type: Number, default: 49832 },
  transactions: [transactionSchema],
  spending: { type: spendingSchema, default: () => ({}) },
  loanEligibility: { type: Number, default: 78 }
});

// Hash password before saving
UserSchema.pre('save', async function() {
  if (!this.isModified('password')) return;
  const salt = await bcrypt.genSalt(10);
  this.password = await bcrypt.hash(this.password, salt);
});

// Compare password method
UserSchema.methods.matchPassword = async function(enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password);
};

module.exports = mongoose.model('User', UserSchema);