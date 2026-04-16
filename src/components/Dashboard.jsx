import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FiActivity,
  FiArrowDownLeft,
  FiArrowUpRight,
  FiBarChart2,
  FiCheckCircle,
  FiClock,
  FiCreditCard,
  FiDollarSign,
  FiHome,
  FiPieChart,
  FiRefreshCw,
  FiShield,
  FiTarget,
  FiTrendingUp,
  FiUser,
  FiChevronLeft,
  FiChevronRight,
  FiCheck,
} from "react-icons/fi";
import { useAuth } from "../context/AuthContext";
import Navbar from "./Navbar";
import { fetchFinancialData, transferMoney, addFunds, dynamicUpdate } from "../services/financialApi";
import "./Dashboard.css";

function useCountUp(target, duration = 1200) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) {
        setValue(target);
        clearInterval(timer);
      } else {
        setValue(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [target, duration]);

  return value;
}

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);

const txStatusClass = (status = "") => {
  const normalized = status.toLowerCase();
  if (normalized === "success" || normalized === "completed") return "completed";
  if (normalized === "blocked") return "blocked-s";
  return "pending";
};

const txIcon = (type = "") => {
  const normalized = type.toLowerCase();
  if (normalized.includes("deposit") || normalized.includes("credit")) return <FiArrowDownLeft />;
  if (normalized.includes("loan")) return <FiCreditCard />;
  if (normalized.includes("transfer")) return <FiArrowUpRight />;
  return <FiActivity />;
};

function Dashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [dashboardData, setDashboardData] = useState({
    balance: 0,
    transactions: [],
    spending: {},
    loanEligibility: 0,
  });
  const [step, setStep] = useState(1);
  const [recipient, setRecipient] = useState("");
  const [amount, setAmount] = useState("");
  const [transferStatus, setTransferStatus] = useState(null);
  const [isTransferring, setIsTransferring] = useState(false);
  const [showAddFundsModal, setShowAddFundsModal] = useState(false);
  const [fundsAmount, setFundsAmount] = useState("");
  const [isAddingFunds, setIsAddingFunds] = useState(false);
  const [loanStep, setLoanStep] = useState(1);
  const [loanAmount, setLoanAmount] = useState("");
  const [loanTenure, setLoanTenure] = useState("");
  const [loanPurpose, setLoanPurpose] = useState("");
  const [monthlyIncome, setMonthlyIncome] = useState("");
  const [employmentType, setEmploymentType] = useState("");
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchFinancialData();
        setDashboardData(data);
      } catch (err) {
        console.error("Failed to load financial data", err);
      }
    };
    loadData();

    const interval = setInterval(async () => {
      try {
        const updated = await dynamicUpdate();
        setDashboardData(prev => ({ ...prev, ...updated }));
      } catch (err) {
        console.error("Dynamic update failed", err);
      }
    }, 120000);

    return () => clearInterval(interval);
  }, []);

  const animatedBalance = useCountUp(dashboardData.balance, 1400);
  const animatedEligibility = useCountUp(dashboardData.loanEligibility, 1000);
  const spendingEntries = Object.entries(dashboardData.spending);
  const maxSpend = spendingEntries.reduce((max, [, value]) => Math.max(max, value), 1);
  const totalMonthlySpend = spendingEntries.reduce((sum, [, value]) => sum + value, 0);
  const firstName = user?.fullName?.split(" ")[0] || "Client";
  const greetingDate = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  const handleTransfer = async (event) => {
    event.preventDefault();
    if (step === 1) {
      if (!recipient) return;
      setStep(2);
      return;
    }
    if (step === 2) {
      if (!amount || parseFloat(amount) <= 0) return;
      setStep(3);
      return;
    }
    setIsTransferring(true);
    try {
      await transferMoney(recipient, parseFloat(amount));
      setTransferStatus({
        success: true,
        message: `${formatCurrency(parseFloat(amount))} has been transferred to ${recipient}.`,
      });
      const newData = await fetchFinancialData();
      setDashboardData(newData);
      setTimeout(() => {
        setStep(1);
        setRecipient("");
        setAmount("");
        setTransferStatus(null);
      }, 3000);
    } catch (error) {
      setTransferStatus({ success: false, message: error.response?.data?.msg || error.message });
      setTimeout(() => setTransferStatus(null), 3000);
    } finally {
      setIsTransferring(false);
    }
  };

  const resetWizard = () => {
    setStep(1);
    setRecipient("");
    setAmount("");
    setTransferStatus(null);
  };

  const resetLoanApp = () => {
    setLoanStep(1);
    setLoanAmount("");
    setLoanTenure("");
    setLoanPurpose("");
    setMonthlyIncome("");
    setEmploymentType("");
    setAiAnalysis(null);
  };

  const runAIAnalysis = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      const income = parseFloat(monthlyIncome) || 0;
      const requestedAmount = parseFloat(loanAmount) || 0;
      const tenure = parseFloat(loanTenure) || 1;
      const monthlyEmi = (requestedAmount * 0.105) / 12 / (1 - Math.pow(1 + 0.105/12, -tenure*12)) || 0;
      const debtToIncome = (monthlyEmi / income) * 100 || 0;
      const approved = income > 20000 && debtToIncome < 40 && requestedAmount <= 200000;
      setAiAnalysis({
        approved,
        score: approved ? 78 : 45,
        incomeScore: income > 50000 ? "High" : income > 25000 ? "Medium" : "Low",
        debtRatio: debtToIncome < 20 ? "Low" : debtToIncome < 40 ? "Moderate" : "High",
        spendingPattern: "Stable",
        accountAge: "2+ years",
        explanation: approved
          ? [
              "Consistent income pattern over the last 12 months",
              "Low debt-to-income ratio of " + Math.round(debtToIncome) + "%",
              "No missed payments in your transaction history",
              "Healthy savings balance relative to the requested amount",
            ]
          : [
              "Income insufficient for requested loan amount",
              "Debt-to-income ratio exceeds 40%",
              "Short account history (less than 6 months)",
              "Erratic spending pattern detected",
            ],
      });
      setIsAnalyzing(false);
      setLoanStep(4);
    }, 1500);
  };

  const handleAddFunds = async () => {
    if (!fundsAmount || parseFloat(fundsAmount) <= 0) {
      alert("Please enter a valid amount");
      return;
    }
    setIsAddingFunds(true);
    try {
      await addFunds(parseFloat(fundsAmount));
      const newData = await fetchFinancialData();
      setDashboardData(newData);
      setShowAddFundsModal(false);
      setFundsAmount("");
    } catch (error) {
      alert(error.response?.data?.msg || "Failed to add funds");
    } finally {
      setIsAddingFunds(false);
    }
  };

  const renderDashboardOverview = () => (
    <div className="dashboard-overview">
      <section className="overview-hero glass-panel">
        <div className="overview-copy">
          <div className="eyebrow">Primary banking dashboard</div>
          <h1>Welcome back, {firstName}</h1>
          <p>
            Review balances, track cash flow, and act on account activity from one
            professional workspace.
          </p>
          <div className="hero-meta">
            <div className="hero-meta-chip">
              <FiClock />
              <span>{greetingDate}</span>
            </div>
            <div className="hero-meta-chip">
              <FiShield />
              <span>Security monitoring active</span>
            </div>
          </div>
        </div>
        <div className="overview-spotlight">
          <div className="spotlight-card main-balance">
            <div className="spotlight-header">
              <span>Available balance</span>
              <FiDollarSign />
            </div>
            <div className="spotlight-value">{formatCurrency(animatedBalance)}</div>
            <div className="spotlight-trend positive">
              <FiTrendingUp />
              <span>12.5% above last month</span>
            </div>
          </div>
          <div className="spotlight-grid">
            <div className="spotlight-card">
              <span className="mini-label">Monthly outflow</span>
              <strong>{formatCurrency(totalMonthlySpend)}</strong>
              <p>Across your tracked categories</p>
            </div>
            <div className="spotlight-card">
              <span className="mini-label">Account standing</span>
              <strong>Excellent</strong>
              <p>No irregular activity detected</p>
            </div>
          </div>
        </div>
      </section>
      <section className="stats-grid">
        <article className="balance-card glass-panel">
          <div className="card-headline">
            <div>
              <div className="card-label">Portfolio snapshot</div>
              <h2>Core account</h2>
            </div>
            <div className="headline-icon">
              <FiBarChart2 />
            </div>
          </div>
          <div className="balance-amount">{formatCurrency(animatedBalance)}</div>
          <p className="balance-text">
            Liquidity remains healthy, with stable incoming deposits and controlled
            outflows this cycle.
          </p>
          <div className="metric-pill-row">
            <div className="metric-pill">
              <span>Daily limit</span>
              <strong>{formatCurrency(100000)}</strong>
            </div>
            <div className="metric-pill">
              <span>Pending settlements</span>
              <strong>02</strong>
            </div>
          </div>
          <button className="add-funds-btn" onClick={() => setShowAddFundsModal(true)}>
            Add funds
          </button>
        </article>
        <article className="eligibility-card glass-panel">
          <div className="card-headline">
            <div>
              <div className="card-label">Credit readiness</div>
              <h2>Loan eligibility</h2>
            </div>
            <div className="headline-icon violet">
              <FiShield />
            </div>
          </div>
          <div className="eligibility-percent">{animatedEligibility}%</div>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${dashboardData.loanEligibility}%` }} />
          </div>
          <p>
            You remain pre-qualified for competitive lending offers. Consistent
            transfers and healthy balances support your current score.
          </p>
        </article>
      </section>
      <section className="quick-actions">
        {[
          { icon: <FiArrowUpRight />, label: "Move money", text: "Transfer instantly", tab: "transfer" },
          { icon: <FiCreditCard />, label: "Manage loans", text: "Check offers and dues", tab: "loans" },
          { icon: <FiRefreshCw />, label: "Activity", text: "View full transaction history", tab: "history" },
          { icon: <FiPieChart />, label: "Insights", text: "Review spending intelligence", tab: "insights" },
        ].map(({ icon, label, text, tab }, index) => (
          <button
            key={tab}
            className="quick-card glass-panel"
            onClick={() => setActiveTab(tab)}
            style={{ "--delay": `${index * 80}ms` }}
          >
            <div className="quick-card-icon">{icon}</div>
            <div className="quick-card-body">
              <span className="quick-card-label">{label}</span>
              <p>{text}</p>
            </div>
          </button>
        ))}
      </section>
      <section className="dashboard-detail-grid">
        <div className="lower-grid">
          <article className="section-card glass-panel">
            <div className="section-title">
              <span>Recent transactions</span>
              <button type="button" className="section-title-link" onClick={() => setActiveTab("history")}>
                View all
              </button>
            </div>
            <div className="tx-list">
              {(dashboardData.transactions.length
                ? dashboardData.transactions.slice(0, 6)
                : Array.from({ length: 4 }, () => ({
                    date: "--",
                    type: "Loading",
                    amount: 0,
                    status: "Pending",
                  }))
              ).map((transaction, index) => (
                <div
                  key={`${transaction.type}-${transaction.date}-${index}`}
                  className={`tx-row${transaction.status === "Blocked" ? " blocked" : ""}`}
                >
                  <div className="tx-icon">{txIcon(transaction.type)}</div>
                  <div className="tx-meta">
                    <div className="tx-type">{transaction.type}</div>
                    <div className="tx-date">{transaction.date}</div>
                  </div>
                  <span className={`tx-status ${txStatusClass(transaction.status)}`}>{transaction.status}</span>
                  <div className={`tx-amount ${transaction.amount > 0 ? "positive" : "negative"}`}>
                    {transaction.amount > 0 ? "+" : "-"}
                    {formatCurrency(Math.abs(transaction.amount))}
                  </div>
                </div>
              ))}
            </div>
          </article>
          <article className="section-card glass-panel">
            <div className="section-title">
              <span>Spending breakdown</span>
            </div>
            <div className="spending-list">
              {spendingEntries.map(([category, value], index) => (
                <div key={category} className="spending-row" style={{ "--delay": `${index * 100}ms` }}>
                  <div className="spending-row-meta">
                    <span className="spending-cat">{category}</span>
                    <span className="spending-val">{formatCurrency(value)}</span>
                  </div>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${Math.min(100, (value / maxSpend) * 100)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </article>
        </div>
        <aside className="advisory-panel glass-panel">
          <div className="section-title">
            <span>Relationship summary</span>
          </div>
          <div className="advisory-item">
            <div className="advisory-icon">
              <FiCheckCircle />
            </div>
            <div>
              <h3>Payment reliability</h3>
              <p>Your repayment and transfer patterns remain consistent.</p>
            </div>
          </div>
          <div className="advisory-item">
            <div className="advisory-icon">
              <FiTarget />
            </div>
            <div>
              <h3>Opportunity</h3>
              <p>Reducing discretionary spend by 10% can free more monthly liquidity.</p>
            </div>
          </div>
          <div className="advisory-item">
            <div className="advisory-icon">
              <FiUser />
            </div>
            <div>
              <h3>Dedicated support</h3>
              <p>Priority servicing is available for lending and card management.</p>
            </div>
          </div>
        </aside>
      </section>
    </div>
  );

  const renderTransferWizard = () => (
    <div className="transfer-wizard">
      <div className="wizard-card glass-panel">
        <div className="wizard-header">
          <h2>Send money</h2>
          <p>Complete secure account-to-account transfers with guided verification.</p>
        </div>
        <div className="wizard-steps">
          {["Recipient", "Amount", "Confirm"].map((label, index) => {
            const stepNumber = index + 1;
            const isDone = step > stepNumber;
            const isActive = step === stepNumber;
            return (
              <React.Fragment key={stepNumber}>
                {index > 0 && <div className={`wstep-line${isDone ? " done" : ""}`} />}
                <div className="wstep">
                  <div className={`wstep-dot${isDone ? " done" : isActive ? " active" : ""}`}>
                    {isDone ? "OK" : stepNumber}
                  </div>
                  <div className={`wstep-label${isActive ? " active-lbl" : ""}`}>{label}</div>
                </div>
              </React.Fragment>
            );
          })}
        </div>
        {transferStatus && (
          <div className={`transfer-status ${transferStatus.success ? "success" : "error"}`}>
            {transferStatus.message}
          </div>
        )}
        <form onSubmit={handleTransfer}>
          {step === 1 && (
            <div className="step-body">
              <label className="step-label">Recipient email</label>
              <input
                className="wizard-input"
                type="email"
                placeholder="name@company.com"
                value={recipient}
                onChange={(event) => setRecipient(event.target.value)}
                required
                autoFocus
              />
              <div className="wizard-actions wizard-actions-right">
                <button className="btn-primary" type="submit">Continue</button>
              </div>
            </div>
          )}
          {step === 2 && (
            <div className="step-body">
              <label className="step-label">Amount (INR)</label>
              <input
                className="wizard-input"
                type="number"
                placeholder="0.00"
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
                required
                min="1"
                autoFocus
              />
              <div className="wizard-actions">
                <button className="btn-ghost" type="button" onClick={() => setStep(1)}>Back</button>
                <button className="btn-primary" type="submit">Continue</button>
              </div>
            </div>
          )}
          {step === 3 && (
            <div className="step-body">
              <label className="step-label">Review and confirm</label>
              <div className="confirm-summary">
                <div className="confirm-row">
                  <span className="confirm-row-label">Recipient</span>
                  <span className="confirm-row-value">{recipient}</span>
                </div>
                <div className="confirm-row">
                  <span className="confirm-row-label">Transfer amount</span>
                  <span className="confirm-row-value big">{formatCurrency(parseFloat(amount || 0))}</span>
                </div>
              </div>
              <div className="wizard-actions">
                <button className="btn-ghost" type="button" onClick={() => setStep(2)}>Back</button>
                <button className="btn-primary" type="submit" disabled={isTransferring}>
                  {isTransferring ? "Processing..." : "Send now"}
                </button>
              </div>
            </div>
          )}
        </form>
        {(step !== 1 || transferStatus) && (
          <button type="button" onClick={resetWizard} className="btn-ghost reset-button">
            Start over
          </button>
        )}
      </div>
    </div>
  );

  const renderLoanWizard = () => (
    <div className="loan-wizard-container">
      <div className="history-header">
        <h2>Loan Application</h2>
        <p>Apply for a loan with AI-powered approval in seconds.</p>
      </div>
      <div className="loan-wizard glass-panel">
        <div className="loan-steps">
          {["Loan Details", "Income Info", "AI Analysis", "Result"].map((label, idx) => {
            const stepNum = idx + 1;
            const isActive = loanStep === stepNum;
            const isDone = loanStep > stepNum;
            return (
              <React.Fragment key={stepNum}>
                {idx > 0 && <div className={`loan-step-line ${isDone ? "done" : ""}`} />}
                <div className="loan-step">
                  <div className={`loan-step-dot ${isActive ? "active" : isDone ? "done" : ""}`}>
                    {isDone ? <FiCheck /> : stepNum}
                  </div>
                  <div className={`loan-step-label ${isActive ? "active-lbl" : ""}`}>{label}</div>
                </div>
              </React.Fragment>
            );
          })}
        </div>
        {loanStep === 1 && (
          <div className="loan-step-body">
            <div className="loan-form-group">
              <label>Loan Amount (INR)</label>
              <div className="loan-amount-buttons">
                {[50000, 200000, 500000, 1000000].map((amt) => (
                  <button
                    key={amt}
                    type="button"
                    className={`loan-amount-btn ${parseFloat(loanAmount) === amt ? "active" : ""}`}
                    onClick={() => setLoanAmount(amt.toString())}
                  >
                    ₹{amt.toLocaleString()}
                  </button>
                ))}
              </div>
              <input
                type="number"
                className="wizard-input"
                placeholder="Custom amount"
                value={loanAmount}
                onChange={(e) => setLoanAmount(e.target.value)}
              />
            </div>
            <div className="loan-form-group">
              <label>Tenure (years)</label>
              <div className="loan-tenure-buttons">
                {[1, 2, 3, 4, 5].map((year) => (
                  <button
                    key={year}
                    type="button"
                    className={`loan-tenure-btn ${parseFloat(loanTenure) === year ? "active" : ""}`}
                    onClick={() => setLoanTenure(year.toString())}
                  >
                    {year} {year === 1 ? "year" : "years"}
                  </button>
                ))}
              </div>
            </div>
            <div className="loan-form-group">
              <label>Purpose</label>
              <select
                className="wizard-input"
                value={loanPurpose}
                onChange={(e) => setLoanPurpose(e.target.value)}
              >
                <option value="">Select loan purpose</option>
                <option value="Home">Home</option>
                <option value="Car">Car</option>
                <option value="Education">Education</option>
                <option value="Personal">Personal</option>
                <option value="Business">Business</option>
              </select>
            </div>
            {loanAmount && loanTenure && (
              <div className="estimated-emi">
                <span>ESTIMATED MONTHLY EMI</span>
                <strong>
                  ₹
                  {Math.round(
                    (parseFloat(loanAmount) * 0.105) /
                      12 /
                      (1 - Math.pow(1 + 0.105 / 12, -parseFloat(loanTenure) * 12))
                  ).toLocaleString()}
                </strong>
                <small>at 10.5% p.a. for {loanTenure} years</small>
              </div>
            )}
            <div className="wizard-actions">
              <button
                className="btn-primary"
                onClick={() => {
                  if (loanAmount && loanTenure && loanPurpose) setLoanStep(2);
                }}
                disabled={!loanAmount || !loanTenure || !loanPurpose}
              >
                Continue <FiChevronRight />
              </button>
            </div>
          </div>
        )}
        {loanStep === 2 && (
          <div className="loan-step-body">
            <div className="loan-form-group">
              <label>Monthly Income (INR)</label>
              <input
                type="number"
                className="wizard-input"
                placeholder="e.g. 60000"
                value={monthlyIncome}
                onChange={(e) => setMonthlyIncome(e.target.value)}
              />
            </div>
            <div className="loan-form-group">
              <label>Employment Type</label>
              <select
                className="wizard-input"
                value={employmentType}
                onChange={(e) => setEmploymentType(e.target.value)}
              >
                <option value="">Select employment type</option>
                <option value="Salaried">Salaried</option>
                <option value="Self-employed">Self-employed</option>
                <option value="Business">Business</option>
                <option value="Freelancer">Freelancer</option>
              </select>
            </div>
            <div className="wizard-actions">
              <button className="btn-ghost" onClick={() => setLoanStep(1)}>
                <FiChevronLeft /> Back
              </button>
              <button
                className="btn-primary"
                onClick={runAIAnalysis}
                disabled={!monthlyIncome || !employmentType || isAnalyzing}
              >
                {isAnalyzing ? "Analyzing..." : "Run AI Analysis"}
              </button>
            </div>
          </div>
        )}
        {loanStep === 3 && (
          <div className="loan-step-body ai-analysis">
            {isAnalyzing ? (
              <div className="ai-loading">
                <div className="spinner"></div>
                <p>AI is analyzing your financial profile...</p>
              </div>
            ) : (
              aiAnalysis && (
                <>
                  <div className="ai-score">
                    <div className="score-circle" style={{ "--score": aiAnalysis.score }}>
                      <span>{aiAnalysis.score}%</span>
                    </div>
                    <h3>Approval Probability</h3>
                  </div>
                  <div className="ai-metrics">
                    <div className="metric">
                      <span>Income Score</span>
                      <strong>{aiAnalysis.incomeScore}</strong>
                    </div>
                    <div className="metric">
                      <span>Debt Ratio</span>
                      <strong>{aiAnalysis.debtRatio}</strong>
                    </div>
                    <div className="metric">
                      <span>Spending Pattern</span>
                      <strong>{aiAnalysis.spendingPattern}</strong>
                    </div>
                    <div className="metric">
                      <span>Account Age</span>
                      <strong>{aiAnalysis.accountAge}</strong>
                    </div>
                  </div>
                  <div className="wizard-actions">
                    <button className="btn-ghost" onClick={() => setLoanStep(2)}>
                      <FiChevronLeft /> Back
                    </button>
                    <button className="btn-primary" onClick={() => setLoanStep(4)}>
                      See Result <FiChevronRight />
                    </button>
                  </div>
                </>
              )
            )}
          </div>
        )}
        {loanStep === 4 && aiAnalysis && (
          <div className="loan-step-body result">
            <div className={`result-badge ${aiAnalysis.approved ? "approved" : "rejected"}`}>
              {aiAnalysis.approved ? "Loan Approved!" : "Loan Declined"}
            </div>
            {aiAnalysis.approved && (
              <p className="result-message">
                Congratulations! Your loan of ₹{parseFloat(loanAmount).toLocaleString()} has been approved.
              </p>
            )}
            <div className="ai-explanation">
              <h4>AI Explanation</h4>
              <ul>
                {aiAnalysis.explanation.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>
            <button className="btn-ghost reset-button" onClick={resetLoanApp}>
              Start New Application
            </button>
          </div>
        )}
      </div>
    </div>
  );

  const renderHistory = () => (
    <div>
      <div className="history-header">
        <h2>Transaction history</h2>
        <p>Review a complete record of posted and reviewed account activity.</p>
      </div>
      <div className="section-card glass-panel">
        <div className="tx-list">
          {dashboardData.transactions.map((transaction, index) => (
            <div
              key={`${transaction.type}-${transaction.date}-${index}`}
              className={`tx-row${transaction.status === "Blocked" ? " blocked" : ""}`}
            >
              <div className="tx-icon">{txIcon(transaction.type)}</div>
              <div className="tx-meta">
                <div className="tx-type">{transaction.type}</div>
                <div className="tx-date">{transaction.date}</div>
              </div>
              <span className={`tx-status ${txStatusClass(transaction.status)}`}>{transaction.status}</span>
              <div className={`tx-amount ${transaction.amount > 0 ? "positive" : "negative"}`}>
                {transaction.amount > 0 ? "+" : "-"}
                {formatCurrency(Math.abs(transaction.amount))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderInsights = () => (
    <div>
      <div className="insights-header">
        <h2>Financial insights</h2>
        <p>Personalized guidance designed to improve liquidity, savings, and control.</p>
      </div>
      <div className="insight-grid">
        {[
          {
            color: "orange",
            icon: <FiTrendingUp />,
            title: "Spending trend",
            text: (
              <>
                Monthly discretionary outflow is <span className="insight-highlight">12% higher</span> than the previous cycle. A quick review of subscriptions may improve surplus cash.
              </>
            ),
          },
          {
            color: "cyan",
            icon: <FiTarget />,
            title: "Savings goal",
            text: (
              <>
                You are <span className="insight-highlight">60% toward your {formatCurrency(50000)} target</span> and currently tracking ahead of schedule.
              </>
            ),
          },
          {
            color: "green",
            icon: <FiShield />,
            title: "Security status",
            text: (
              <>
                Recent monitoring shows <span className="insight-highlight">no suspicious activity</span> across your latest transactions.
              </>
            ),
          },
          {
            color: "purple",
            icon: <FiPieChart />,
            title: "Smart recommendation",
            text: (
              <>
                Trimming dining and lifestyle spend by 20% may preserve <span className="insight-highlight">{formatCurrency(2500)} per month</span> for short-term goals and emergency reserves.
              </>
            ),
          },
        ].map(({ color, icon, title, text }) => (
          <div key={title} className={`insight-card ${color} glass-panel`}>
            <div className="insight-icon">{icon}</div>
            <div className="insight-title">{title}</div>
            <div className="insight-text">{text}</div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="dashboard-container">
      <div className="dashboard-bg dashboard-bg-one" />
      <div className="dashboard-bg dashboard-bg-two" />
      <Navbar />
      <div className="dashboard-content">
        <div className="dashboard-back-button">
          <Link to="/">
            <FiHome />
            <span>Back to home</span>
          </Link>
        </div>
        <div className="dashboard-tabs glass-panel">
          {[
            { id: "dashboard", label: "Overview" },
            { id: "transfer", label: "Transfer" },
            { id: "loans", label: "Loans" },
            { id: "history", label: "History" },
            { id: "insights", label: "Insights" },
          ].map(({ id, label }) => (
            <button key={id} className={activeTab === id ? "tab-active" : ""} onClick={() => setActiveTab(id)}>
              {label}
            </button>
          ))}
        </div>
        <div className="tab-pane" key={activeTab}>
          {activeTab === "dashboard" && renderDashboardOverview()}
          {activeTab === "transfer" && renderTransferWizard()}
          {activeTab === "loans" && renderLoanWizard()}
          {activeTab === "history" && renderHistory()}
          {activeTab === "insights" && renderInsights()}
        </div>
      </div>

      {showAddFundsModal && (
        <div className="modal-overlay" onClick={() => setShowAddFundsModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Add Funds</h3>
            <input
              type="number"
              placeholder="Amount in ₹"
              value={fundsAmount}
              onChange={(e) => setFundsAmount(e.target.value)}
              autoFocus
            />
            <div className="modal-actions">
              <button className="btn-ghost" onClick={() => setShowAddFundsModal(false)}>Cancel</button>
              <button className="btn-primary" onClick={handleAddFunds} disabled={isAddingFunds}>
                {isAddingFunds ? 'Processing...' : 'Deposit'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;