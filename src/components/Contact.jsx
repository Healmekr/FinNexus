import React from "react";
import { Link } from "react-router-dom";
import { FiMapPin, FiPhone, FiMail as FiMailIcon, FiClock, FiMessageCircle, FiArrowLeft } from "react-icons/fi";
import Navbar from "./Navbar";
import "./Contact.css";

function Contact() {
  return (
    <div className="contact-page">
      {/* Floating blurs (exactly like Dashboard) */}
      <div className="contact-bg contact-bg-one" />
      <div className="contact-bg contact-bg-two" />

      <Navbar hideHowItWorks={true} />
      <div className="contact-back-button">
        <Link to="/">
          <FiArrowLeft size={18} /> Back to Home
        </Link>
      </div>
      <div className="contact-container">
        <div className="contact-header">
          <h1 className="contact-title">Contact Us</h1>
          <p className="contact-subtitle">We're here to help — reach out anytime</p>
        </div>
        <div className="contact-grid">
          <div className="contact-card">
            <div className="contact-icon"><FiMapPin /></div>
            <h3>Visit Us</h3>
            <p>123 FinNexus Tower<br />Silicon Valley, CA 94025<br />United States</p>
          </div>
          <div className="contact-card">
            <div className="contact-icon"><FiPhone /></div>
            <h3>Call Us</h3>
            <p>+1 (800) 123-4567<br />+1 (650) 987-6543<br />Mon-Fri, 9AM - 6PM PST</p>
          </div>
          <div className="contact-card">
            <div className="contact-icon"><FiMailIcon /></div>
            <h3>Email Us</h3>
            <p>support@finnexus.com<br />careers@finnexus.com<br />press@finnexus.com</p>
          </div>
          <div className="contact-card">
            <div className="contact-icon"><FiClock /></div>
            <h3>Business Hours</h3>
            <p>Monday – Friday: 9:00 AM – 6:00 PM<br />Saturday: 10:00 AM – 2:00 PM<br />Sunday: Closed</p>
          </div>
        </div>
        <div className="contact-chat">
          <FiMessageCircle />
          <span>Live chat available 24/7 — click the chat bubble</span>
        </div>
      </div>
    </div>
  );
}

export default Contact;