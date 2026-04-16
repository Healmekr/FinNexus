// src/services/mockData.js

class MockDataService {
  constructor() {
    this.balance = 49832; // starting balance in PHP
    this.transactions = [
      { date: '2026-03-03', type: 'Transfer', amount: -2500, status: 'Success' },
      { date: '2026-03-02', type: 'Deposit', amount: 15000, status: 'Success' },
      { date: '2026-03-01', type: 'Transfer', amount: -800, status: 'Success' },
      { date: '2026-02-28', type: 'Loan EMI', amount: -5200, status: 'Success' },
      { date: '2026-02-27', type: 'Transfer', amount: -12000, status: 'Blocked' },
    ];
    this.spending = {
      Food: 12000,
      Transport: 9000,
      Shopping: 6000,
      Bills: 3000,
      Entertainment: 0,
    };
    this.loanEligibility = 78; // percentage
    this.listeners = [];
    this.interval = null;
    this.startDynamicUpdates();
  }

  // Subscribe to balance changes
  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  notify() {
    this.listeners.forEach(cb => cb({
      balance: this.balance,
      transactions: this.transactions,
      spending: this.spending,
      loanEligibility: this.loanEligibility,
    }));
  }

  // Random fluctuation every 2-3 minutes
  startDynamicUpdates() {
    this.interval = setInterval(() => {
      const change = Math.floor(Math.random() * 201) - 100; // -100 to +100
      this.balance = Math.max(0, this.balance + change);
      // Add a random transaction entry for realism
      const newTransaction = {
        date: new Date().toISOString().slice(0,10),
        type: change > 0 ? 'Deposit' : 'Transfer',
        amount: change,
        status: Math.random() > 0.9 ? 'Blocked' : 'Success',
      };
      this.transactions.unshift(newTransaction);
      if (this.transactions.length > 10) this.transactions.pop();
      // Slightly adjust spending categories randomly
      const categories = Object.keys(this.spending);
      const randomCat = categories[Math.floor(Math.random() * categories.length)];
      this.spending[randomCat] = Math.max(0, this.spending[randomCat] + Math.floor(change * 0.2));
      this.notify();
    }, 120000); // 2 minutes
  }

  stopDynamicUpdates() {
    if (this.interval) clearInterval(this.interval);
  }

  // Transfer money (returns success/failure)
  transfer(recipientEmail, amount) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (amount > this.balance) {
          reject(new Error('Insufficient balance'));
        } else if (amount <= 0) {
          reject(new Error('Invalid amount'));
        } else {
          this.balance -= amount;
          const newTransaction = {
            date: new Date().toISOString().slice(0,10),
            type: `Transfer to ${recipientEmail}`,
            amount: -amount,
            status: 'Success',
          };
          this.transactions.unshift(newTransaction);
          if (this.transactions.length > 10) this.transactions.pop();
          this.notify();
          resolve({ success: true, newBalance: this.balance });
        }
      }, 500);
    });
  }
}

export const mockData = new MockDataService();