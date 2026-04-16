import React, { useEffect, useRef } from "react";
import FlipCard from "./FlipCard";
import { AiOutlineSafety, AiOutlinePieChart } from "react-icons/ai";
import { MdOutlineAnalytics } from "react-icons/md";
import { FiUserPlus, FiFileText, FiCpu, FiArrowRight } from "react-icons/fi";
import "./FeaturesAndHowItWorks.css";

const FeaturesAndHowItWorks = () => {
  const cardsData = [
    {
      title: "AI Loan Analysis",
      description: "Get personalized approval predictions with clear, transparent explanations powered by machine learning.",
      icon: <MdOutlineAnalytics size={48} color="#7c3aed" />,
    },
    {
      title: "Fraud Protection",
      description: "Real-time detection of suspicious activity keeps your accounts and transactions safe around the clock.",
      icon: <AiOutlineSafety size={48} color="#7c3aed" />,
    },
    {
      title: "Financial Insights",
      description: "Understand your spending patterns and get actionable advice to improve your financial health score.",
      icon: <AiOutlinePieChart size={48} color="#7c3aed" />,
    },
  ];

  const steps = [
    {
      icon: <FiUserPlus />,
      number: "01",
      title: "Build Your Profile",
      description:
        "Start making transactions and let our AI learn your financial patterns to build a comprehensive profile.",
      gradient: "linear-gradient(135deg, #00eaff, #0077ff)",
    },
    {
      icon: <FiFileText />,
      number: "02",
      title: "Apply for a Loan",
      description:
        "Submit a loan application with just one click. Our AI instantly evaluates your eligibility.",
      gradient: "linear-gradient(135deg, #7c3aed, #a855f7)",
    },
    {
      icon: <FiCpu />,
      number: "03",
      title: "Get AI-Powered Approval",
      description:
        "Receive your approval decision with personalized advice and clear explanations — no hidden criteria.",
      gradient: "linear-gradient(135deg, #f59e0b, #ef4444)",
    },
  ];

  const stepRefs = useRef([]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
          }
        });
      },
      { threshold: 0.2 }
    );

    stepRefs.current.forEach((ref) => {
      if (ref) observer.observe(ref);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <div className="features-howitworks">
      {/* Floating blurs (exactly like Dashboard) */}
      <div className="features-bg features-bg-one" />
      <div className="features-bg features-bg-two" />

      {/* Card Section */}
      <div className="card-section">
        <div className="card-section-header">
          <h1>Everything You Need for Smarter Banking</h1>
          <p>Powered by advanced AI to give you the edge in financial management.</p>
        </div>
        <div className="cards-container">
          {cardsData.map((card, index) => (
            <FlipCard key={index} title={card.title} description={card.description} icon={card.icon} />
          ))}
        </div>
      </div>

      {/* How It Works Section */}
      <div className="howitworks-section" id="how-it-works">
        <div className="hiw-header">
          <h1 className="hiw-title">How It Works</h1>
          <p className="hiw-subtitle">Three simple steps to smarter banking.</p>
        </div>

        <div className="steps-container">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className="step-card"
              ref={(el) => (stepRefs.current[idx] = el)}
              style={{ transitionDelay: `${idx * 0.1}s` }}
            >
              <div className="step-number" style={{ background: step.gradient }}>
                {step.number}
              </div>
              <div
                className="step-icon"
                style={{
                  color: step.gradient.includes("00eaff")
                    ? "#00eaff"
                    : step.gradient.includes("7c3aed")
                    ? "#a855f7"
                    : "#f59e0b",
                }}
              >
                {step.icon}
              </div>
              <h3 className="step-title">{step.title}</h3>
              <p className="step-description">{step.description}</p>
              <div className="step-arrow">
                <FiArrowRight />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FeaturesAndHowItWorks;