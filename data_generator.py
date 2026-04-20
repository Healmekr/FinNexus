"""
FinNexus Data Generator
Generates realistic synthetic banking data for:
1. Loan applications
2. Fraud transactions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


class FinNexusDataGenerator:
    """
    Generate synthetic financial data with realistic patterns
    """
    
    def __init__(self, seed=42):
        """
        Initialize generator with random seed for reproducibility
        
        Args:
            seed: Random seed (same seed = same data every time)
        """
        np.random.seed(seed)
        random.seed(seed)
        print(f"Random seed set to {seed} (reproducible results)")
    
    # ==========================================
    # LOAN DATASET GENERATION
    # ==========================================
    
    def generate_loan_dataset(self, n_samples=5000):
        """
        Generate loan application dataset with realistic approval logic
        
        Args:
            n_samples: Number of loan applications to generate
            
        Returns:
            pandas DataFrame with loan applications
        """
        
        print(f"\nGenerating {n_samples} loan applications...")
        
        data = []
        
        for i in range(n_samples):
            
            # ==========================================
            # STEP 1: Basic User Information
            # ==========================================
            
            # Monthly income (log-normal distribution - realistic for salaries)
            # Most people earn ₹30K-50K, some earn ₹20K, few earn ₹100K+
            monthly_income = np.random.lognormal(mean=10.5, sigma=0.5)
            # mean=10.5, sigma=0.5 gives us realistic income distribution
            
            # Account age (how long user has been a customer)
            # Exponential distribution - more new accounts than old
            account_age_months = int(np.random.exponential(scale=12))
            account_age_months =max(1,min(account_age_months, 60)) # Max 5 years
            
            # ==========================================
            # STEP 2: Loan Details
            # ==========================================
            
            loan_amount = np.random.uniform(10000, 500000)  # ₹10K to ₹5L
            loan_tenure = random.choice([6, 12, 18, 24, 36, 48, 60])  # months
            loan_purpose = random.choice([
                'home', 'education', 'business', 'personal', 'medical'
            ])
            
            # ==========================================
            # STEP 3: Financial Behavior (Correlated with Income)
            # ==========================================
            
            # Savings propensity (beta distribution: most save 20-30%)
            savings_propensity = np.random.beta(a=2, b=5)
            # Beta(2,5) creates realistic savings distribution
            
            # High earners tend to save more (add bonus)
            if monthly_income > 60000:
                savings_propensity += 0.1
            
            # Calculate actual savings
            avg_monthly_savings = monthly_income * savings_propensity
            savings_rate = savings_propensity
            
            # Savings consistency (how stable is saving?)
            # Older accounts = more consistent
            base_volatility = np.random.uniform(500, 5000)
            if account_age_months > 24:
                savings_consistency = base_volatility * 0.6  # More stable
            else:
                savings_consistency = base_volatility  # Less stable
            
            # Spending (what's left after saving)
            avg_monthly_spending = monthly_income - avg_monthly_savings
            
            # Spending volatility (younger accounts spend more erratically)
            if account_age_months < 6:
                spending_volatility = np.random.uniform(3000, 8000)
            else:
                spending_volatility = np.random.uniform(1000, 5000)
            
            # ==========================================
            # STEP 4: Transaction History
            # ==========================================
            
            # Transaction count (increases with account age)
            # Poisson distribution: random but realistic count
            base_tx_count = np.random.poisson(lam=account_age_months * 5)
            transaction_count = max(10, min(base_tx_count, 500))
            
            # Average transaction size
            avg_transaction_size = avg_monthly_spending / max(1, transaction_count / account_age_months)
            
            # ==========================================
            # STEP 5: Debt Situation
            # ==========================================
            
            # 40% of users have existing debt
            has_debt = random.random() < 0.4
            
            if has_debt:
                # Debt is correlated with income (can borrow more if earn more)
                existing_debt = np.random.uniform(0, monthly_income * 3)
            else:
                existing_debt = 0
            
            debt_to_income_ratio = existing_debt / monthly_income
            
            # ==========================================
            # STEP 6: Calculate EMI Affordability
            # ==========================================
            
            # EMI = Equated Monthly Installment
            # Formula: EMI = [P × r × (1+r)^n] / [(1+r)^n - 1]
            # where P = loan amount, r = monthly rate, n = tenure
            
            interest_rate = 0.10  # 10% annual interest
            monthly_rate = interest_rate / 12
            n_payments = loan_tenure
            
            if n_payments > 0:
                # Calculate EMI using compound interest formula
                emi = (loan_amount * monthly_rate * (1 + monthly_rate)**n_payments) / \
                      ((1 + monthly_rate)**n_payments - 1)
            else:
                emi = loan_amount
            
            emi_to_income_ratio = emi / monthly_income
            # This tells us: "EMI is X% of monthly income"
            # If EMI is 50% of income → user can't afford it!
            
            # ==========================================
            # STEP 7: APPROVAL DECISION (Business Logic)
            # ==========================================
            
            # We use a scoring system (like real banks)
            approval_score = 50  # Start with neutral score
            
            # Factor 1: Income adequacy (+20 max)
            if monthly_income > 50000:
                approval_score += 20  # High income
            elif monthly_income > 30000:
                approval_score += 10  # Medium income
            # else: no points (low income)
            
            # Factor 2: EMI affordability (+25 max)
            # Rule: EMI should be < 40% of income
            if emi_to_income_ratio < 0.25:
                approval_score += 25  # Very affordable
            elif emi_to_income_ratio < 0.35:
                approval_score += 15  # Affordable
            elif emi_to_income_ratio < 0.45:
                approval_score += 5   # Barely affordable
            else:
                approval_score -= 10  # Too expensive!
            
            # Factor 3: Savings habit (+20 max)
            if savings_rate > 0.20:
                approval_score += 20  # Good saver (>20%)
            elif savings_rate > 0.10:
                approval_score += 10  # Moderate saver (>10%)
            
            # Factor 4: Debt burden (+20 max)
            # Rule: Debt should be < 40% of annual income
            if debt_to_income_ratio < 0.3:
                approval_score += 20  # Low debt
            elif debt_to_income_ratio < 0.5:
                approval_score += 10  # Moderate debt
            else:
                approval_score -= 5   # High debt (risky!)
            
            # Factor 5: Account maturity (+10 max)
            if account_age_months > 12:
                approval_score += 10  # Established customer
            elif account_age_months > 6:
                approval_score += 5   # Decent history
            
            # Factor 6: Transaction activity (+5 max)
            if transaction_count > 50:
                approval_score += 5   # Active user
            
            # Factor 7: Spending stability (+10 max)
            if spending_volatility < 3000:
                approval_score += 10  # Stable spender
            elif spending_volatility < 5000:
                approval_score += 5   # Moderately stable
            
            # Add random noise (life isn't perfectly predictable!)
            noise = np.random.normal(0, 8)  # Random ±8 points
            final_score = approval_score + noise
            
            # Decision threshold
            # Score > 70 → Approve
            # Score ≤ 70 → Reject
            approved = 1 if final_score >= 70 else 0
            
            # ==========================================
            # STEP 8: Store Record
            # ==========================================
            
            data.append({
                'user_id': f'USER_{i:05d}',
                'monthly_income': round(monthly_income, 2),
                'loan_amount': round(loan_amount, 2),
                'loan_tenure': loan_tenure,
                'loan_purpose_encoded': self._encode_purpose(loan_purpose),
                'loan_purpose': loan_purpose,
                'loan_to_income_ratio': round(loan_amount / monthly_income, 4),
                'avg_monthly_savings': round(avg_monthly_savings, 2),
                'savings_rate': round(savings_rate, 4),
                'savings_consistency': round(savings_consistency, 2),
                'avg_monthly_spending': round(avg_monthly_spending, 2),
                'spending_volatility': round(spending_volatility, 2),
                'transaction_count': transaction_count,
                'avg_transaction_size': round(avg_transaction_size, 2),
                'existing_debt': round(existing_debt, 2),
                'debt_to_income_ratio': round(debt_to_income_ratio, 4),
                'account_age_months': account_age_months,
                'emi_to_income_ratio': round(emi_to_income_ratio, 4),
                'emi': round(emi, 2),
                'approval_score': round(final_score, 2),
                'approved': approved
            })
        
        # Convert to DataFrame (table format)
        df = pd.DataFrame(data)
        
        print(f"Generated {len(df)} loan applications")
        print(f"   Approval rate: {df['approved'].mean()*100:.1f}%")
        print(f"   Approved: {df['approved'].sum()}")
        print(f"   Rejected: {(1-df['approved']).sum()}")
        
        return df
    
    def _encode_purpose(self, purpose):
        """Convert loan purpose to numeric code"""
        purpose_map = {
            'home': 1,
            'education': 2,
            'business': 3,
            'personal': 4,
            'medical': 5
        }
        return purpose_map.get(purpose.lower(), 4)
    
    # ==========================================
    # FRAUD DATASET GENERATION
    # ==========================================
    
    def generate_fraud_dataset(self, n_users=1000, days=180):
        """
        Generate realistic fraud transaction dataset
        
        Includes fraud patterns:
        1. Account Takeover (sudden behavior change)
        2. Money Mule (rapid in-out)
        3. Velocity Attack (many txs quickly)
        4. Smurfing (structured amounts)
        5. Dormant Reactivation (inactive → active)
        
        Args:
            n_users: Number of users
            days: Time period to simulate
            
        Returns:
            pandas DataFrame with transactions
        """
        
        print(f"\nGenerating fraud dataset ({n_users} users, {days} days)...")
        
        transactions = []
        tx_id = 0
        
        # Create user profiles
        users = self._create_user_profiles(n_users)
        
        # Simulate transactions day by day
        start_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Each user may transact
            for user in users:
                user_id = user['id']
                
                # Skip if user not active today
                if not self._is_user_active(user, day, current_date):
                    continue
                
                # Check if account is compromised
                is_compromised = user.get('compromised', False)
                compromise_day = user.get('compromise_day', 999)
                
                if is_compromised and day >= compromise_day:
                    # === FRAUD BEHAVIOR ===
                    fraud_type = user['fraud_type']
                    
                    if fraud_type == 'account_takeover':
                        txs = self._generate_account_takeover(user, current_date, tx_id)
                    elif fraud_type == 'money_mule':
                        txs = self._generate_money_mule(user, current_date, tx_id)
                    elif fraud_type == 'velocity_attack':
                        txs = self._generate_velocity_attack(user, current_date, tx_id)
                    elif fraud_type == 'smurfing':
                        txs = self._generate_smurfing(user, current_date, tx_id)
                    elif fraud_type == 'dormant_reactivation':
                        txs = self._generate_dormant_reactivation(user, current_date, tx_id)
                    elif fraud_type == 'ping_attack':
                        txs = self._generate_ping_attack(user, current_date, tx_id)
                    elif fraud_type == 'sequential_escalation':
                        txs = self._generate_sequential_escalation(user, current_date, tx_id)
                    
                    transactions.extend(txs)
                    tx_id += len(txs)
                    
                else:
                    # === NORMAL BEHAVIOR ===
                    num_tx = np.random.poisson(user['avg_daily_tx'])
                    
                    for _ in range(num_tx):
                        tx = self._generate_normal_transaction(user, current_date, tx_id)
                        transactions.append(tx)
                        tx_id += 1
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Add derived features
        df = self._add_fraud_features(df)
        
        print(f"✅ Generated {len(df)} transactions")
        print(f"   Fraud rate: {df['is_fraud'].mean()*100:.2f}%")
        print(f"   Normal: {(1-df['is_fraud']).sum()}")
        print(f"   Fraud: {df['is_fraud'].sum()}")
        print(f"\n   Fraud breakdown:")
        if df['is_fraud'].sum() > 0:
            print(df[df['is_fraud']==1]['fraud_type'].value_counts())
        
        return df
    
    def _create_user_profiles(self, n_users):
        """Create user profiles (95% normal, 5% compromised)"""
        users = []
        n_fraud = int(n_users * 0.05)
        
        fraud_types = [
            'account_takeover', 'money_mule', 'velocity_attack',
            'smurfing', 'dormant_reactivation','ping_attack','sequential_escalation' 
        ]
        
        for i in range(n_users):
            is_fraud_user = i < n_fraud
            
            user = {
                'id': f'USER_{i:04d}',
                'avg_daily_tx': np.random.poisson(2) + 1,  # 1-5 tx/day
                'avg_tx_amount': np.random.lognormal(7.5, 1),  # ₹1K-10K
                'account_age_days': np.random.randint(30, 365),
                'is_active': np.random.random() > 0.1,  # 90% active
                'compromised': is_fraud_user
            }
            
            if is_fraud_user:
                user['fraud_type'] = random.choice(fraud_types)
                user['compromise_day'] = np.random.randint(90, 150)
            
            users.append(user)
        
        return users
    
    def _is_user_active(self, user, day, current_date):
        """Determine if user transacts today"""
        
        # Dormant users inactive until compromise
        if user.get('fraud_type') == 'dormant_reactivation':
            compromise_day = user.get('compromise_day', 999)
            if day < compromise_day:
                return random.random() < 0.01  # 1% dormant activity
            else:
                return random.random() < 0.9   # 90% active after compromise
        
        # Normal activity
        if not user['is_active']:
            return random.random() < 0.1
        
        return random.random() < 0.6  # 60% daily activity
    
    def _generate_normal_transaction(self, user, date, tx_id):
        """Generate normal transaction"""
        
        amount = max(100, np.random.lognormal(
            np.log(user['avg_tx_amount']), 0.5
        ))
        
        hour = int(np.random.normal(14, 4))  # Peak at 2 PM
        hour = max(6, min(23, hour))
        
        return {
            'transaction_id': f'TX_{tx_id:08d}',
            'user_id': user['id'],
            'timestamp': date.replace(hour=hour, minute=random.randint(0, 59)),
            'amount': round(amount, 2),
            'recipient_id': f'USER_{random.randint(0, 999):04d}',
            'is_fraud': 0,
            'fraud_type': None
        }
    
    def _generate_account_takeover(self, user, date, tx_id):
        """Account takeover: sudden large transfers"""
        transactions = []
        num_txs = random.randint(1, 3)
        
        for i in range(num_txs):
            amount = user['avg_tx_amount'] * np.random.uniform(10, 50)
            hour = random.choice(list(range(0, 6)) + list(range(22, 24)))
            
            transactions.append({
                'transaction_id': f'TX_{tx_id + i:08d}',
                'user_id': user['id'],
                'timestamp': date.replace(hour=hour, minute=random.randint(0, 59)),
                'amount': round(amount, 2),
                'recipient_id': f'FRAUDSTER_{random.randint(1, 10):02d}',
                'is_fraud': 1,
                'fraud_type': 'account_takeover'
            })
        
        return transactions
    
    def _generate_money_mule(self, user, date, tx_id):
        """Money mule: receive large → send to multiple"""
        transactions = []
        
        num_recipients = random.randint(3, 5)
        incoming = np.random.uniform(50000, 200000)
        amounts = self._split_amount(incoming * 0.95, num_recipients)
        
        base_hour = random.randint(8, 20)
        
        for i, split_amount in enumerate(amounts):
            transactions.append({
                'transaction_id': f'TX_{tx_id + i:08d}',
                'user_id': user['id'],
                'timestamp': date.replace(hour=base_hour, minute=i * 5),
                'amount': round(split_amount, 2),
                'recipient_id': f'MULE_{random.randint(1, 20):02d}',
                'is_fraud': 1,
                'fraud_type': 'money_mule'
            })
        
        return transactions
    
    def _generate_velocity_attack(self, user, date, tx_id):
        """Velocity attack: many txs rapidly"""
        transactions = []
        num_txs = random.randint(10, 20)
        
        base_hour = random.randint(8, 22)
        base_minute = random.randint(0, 30)
        
        for i in range(num_txs):
            amount = np.random.uniform(1000, 5000)
            
            transactions.append({
                'transaction_id': f'TX_{tx_id + i:08d}',
                'user_id': user['id'],
                'timestamp': date.replace(
                    hour=base_hour,
                    minute=(base_minute + i * 3) % 60
                ),
                'amount': round(amount, 2),
                'recipient_id': f'USER_{random.randint(0, 999):04d}',
                'is_fraud': 1,
                'fraud_type': 'velocity_attack'
            })
        
        return transactions
    
    def _generate_smurfing(self, user, date, tx_id):
        """Smurfing: break large amount into small txs"""
        transactions = []
        
        total = np.random.uniform(100000, 500000)
        threshold = 49000
        num_txs = int(total / threshold) + 1
        
        amounts = self._split_amount(total, num_txs)
        base_hour = random.randint(10, 18)
        
        for i, amount in enumerate(amounts):
            transactions.append({
                'transaction_id': f'TX_{tx_id + i:08d}',
                'user_id': user['id'],
                'timestamp': date.replace(
                    hour=(base_hour + i // 4) % 24,
                    minute=(i * 10) % 60
                ),
                'amount': round(amount, 2),
                'recipient_id': f'SHELL_{random.randint(1, 15):02d}',
                'is_fraud': 1,
                'fraud_type': 'smurfing'
            })
        
        return transactions
    
    def _generate_dormant_reactivation(self, user, date, tx_id):
        """Dormant reactivation: inactive → burst of activity"""
        transactions = []
        num_txs = random.randint(5, 10)
        
        for i in range(num_txs):
            amount = np.random.uniform(5000, 50000)
            
            transactions.append({
                'transaction_id': f'TX_{tx_id + i:08d}',
                'user_id': user['id'],
                'timestamp': date.replace(
                    hour=random.randint(0, 23),
                    minute=random.randint(0, 59)
                ),
                'amount': round(amount, 2),
                'recipient_id': f'USER_{random.randint(0, 999):04d}',
                'is_fraud': 1,
                'fraud_type': 'dormant_reactivation'
            })
        
        return transactions
    
    def _generate_ping_attack(self, user, date, tx_id):
        transactions = []
    
        # PHASE 1: Ping transactions (testing)
        num_pings = random.randint(1, 2)
        ping_hour = random.randint(0, 23)
        ping_minute = random.randint(0, 50)
        
        for i in range(num_pings):
            # Tiny amount (₹1 - ₹10)
            ping_amount = random.uniform(1, 10)
            
            transactions.append({
                'transaction_id': f'TX_{tx_id + i:08d}',
                'user_id': user['id'],
                'timestamp': date.replace(
                    hour=ping_hour,
                    minute=ping_minute + i
                ),
                'amount': round(ping_amount, 2),
                'recipient_id': f'TEST_{random.randint(1, 5):02d}',
                'is_fraud': 1,
                'fraud_type': 'ping_attack',
                'fraud_stage': 'testing'  # NEW: Track attack stage
            })
    
        # PHASE 2: Wait 5-10 minutes, then drain account
        drain_delay = random.randint(5, 10)  # minutes
        
        # Large draining transaction (10-100x normal)
        drain_amount = user['avg_tx_amount'] * np.random.uniform(10, 100)
        
        transactions.append({
            'transaction_id': f'TX_{tx_id + num_pings:08d}',
            'user_id': user['id'],
            'timestamp': date.replace(
                hour=ping_hour,
                minute=ping_minute + drain_delay
            ),
            'amount': round(drain_amount, 2),
            'recipient_id': f'FRAUDSTER_{random.randint(1, 10):02d}',
            'is_fraud': 1,
            'fraud_type': 'ping_attack',
            'fraud_stage': 'execution'  # Attack execution phase
        })
    
        return transactions
    
    def _generate_sequential_escalation(self, user, date, tx_id):
        """
        FRAUD TYPE 7: Sequential Escalation
        
        Pattern:
        Gradually increase transaction amounts to avoid velocity alerts
        Example: ₹5K → wait 10 min → ₹15K → wait 10 min → ₹50K → wait → ₹100K
        
        This bypasses simple "high amount" rules
        """
        transactions = []
        
        # Number of escalation steps (3-5 transactions)
        num_steps = random.randint(3, 5)
        
        # Starting amount (small)
        base_amount = np.random.uniform(2000, 5000)
        
        # Escalation factor (each transaction is 2-3x the previous)
        escalation_factor = np.random.uniform(2, 3)
        
        base_hour = random.randint(8, 20)
        base_minute = random.randint(0, 40)
        
        for i in range(num_steps):
            # Calculate escalated amount
            # Step 0: ₹5K, Step 1: ₹15K, Step 2: ₹45K, etc.
            amount = base_amount * (escalation_factor ** i)
            
            # Time delay between transactions (8-15 minutes)
            time_delay = random.randint(8, 15) * i
            
            transactions.append({
                'transaction_id': f'TX_{tx_id + i:08d}',
                'user_id': user['id'],
                'timestamp': date.replace(
                    hour=base_hour,
                    minute=(base_minute + time_delay) % 60
                ),
                'amount': round(amount, 2),
                'recipient_id': f'MULE_{random.randint(1, 20):02d}',
                'is_fraud': 1,
                'fraud_type': 'sequential_escalation',
                'escalation_step': i + 1  # Track which step in the sequence
            })
        
        return transactions
    
    def _split_amount(self, total, n_parts):
        """Split amount into n parts"""
        parts = np.random.dirichlet(np.ones(n_parts)) * total
        return parts
    
    def _add_fraud_features(self, df):
        """Add derived features for fraud detection"""
        
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Hour of day
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        # Transactions per day
        velocity = df.groupby(['user_id', 'date']).size().reset_index(name='daily_tx_count')
        df = df.merge(velocity, on=['user_id', 'date'], how='left')
        
        # User average amount
        user_avg = df.groupby('user_id')['amount'].mean().reset_index(name='user_avg_amount')
        df = df.merge(user_avg, on='user_id', how='left')
        df['amount_deviation_ratio'] = df['amount'] / df['user_avg_amount']
        
        # Time since last transaction
        df['prev_timestamp'] = df.groupby('user_id')['timestamp'].shift(1)
        df['time_since_last_tx_minutes'] = (
            pd.to_datetime(df['timestamp']) - pd.to_datetime(df['prev_timestamp'])
        ).dt.total_seconds() / 60
        df['time_since_last_tx_minutes'].fillna(1440, inplace=True)
        
        # Round amount flag
        df['is_round_amount'] = (df['amount'] % 10000 == 0).astype(int)
        
        # Recipient frequency
        recipient_counts = df.groupby(['user_id', 'recipient_id']).size().reset_index(name='recipient_frequency')
        df = df.merge(recipient_counts, on=['user_id', 'recipient_id'], how='left')
        df['is_new_recipient'] = (df['recipient_frequency'] == 1).astype(int)
        
        return df
    
    # ==========================================
    # SAVE DATASETS
    # ==========================================
    
    def save_all_datasets(self):
        """Generate and save both datasets"""
        
        print("\n" + "="*60)
        print(" FINNEXUS DATA GENERATION")
        print("="*60)
        
        # Generate loan data
        loan_df = self.generate_loan_dataset(n_samples=5000)
        loan_df.to_csv('data/loan_applications.csv', index=False)
        print(f"\n Saved: data/loan_applications.csv")
        
        # Generate fraud data
        fraud_df = self.generate_fraud_dataset(n_users=1000, days=180)
        fraud_df.to_csv('data/fraud_transactions.csv', index=False)
        print(f" Saved: data/fraud_transactions.csv")
        
        print("\n" + "="*60)
        print(" DATA GENERATION COMPLETE")
        print("="*60)
        print("\nNext steps:")
        print("1. Open Jupyter Notebook")
        print("2. Run: jupyter notebook")
        print("3. Start training models!")
        
        return loan_df, fraud_df


# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == '__main__':
    # Create generator
    generator = FinNexusDataGenerator(seed=42)
    
    # Generate and save all data
    loan_df, fraud_df = generator.save_all_datasets()