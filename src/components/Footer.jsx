import React from "react";
import { FaInstagram, FaTwitter, FaLinkedin } from "react-icons/fa";
import logo from "../images/fnlogo.png";
import "./Footer.css";

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-left">
          <img src={logo} alt="FinNexus" className="footer-logo" />
        </div>
        <div className="footer-center">
          <p className="copyright">© 2026 FinNexus. All rights reserved.</p>
        </div>
        <div className="footer-right">
          <a 
            href="https://www.instagram.com/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="social-link"
          >
            <FaInstagram size={22} />
          </a>
          <a 
            href="https://www.twitter.com/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="social-link"
          >
            <FaTwitter size={22} />
          </a>
          <a 
            href="https://www.linkedin.com/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="social-link"
          >
            <FaLinkedin size={22} />
          </a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;