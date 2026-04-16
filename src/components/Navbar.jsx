import React, { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { FiHelpCircle, FiBarChart2, FiLogIn, FiUserPlus, FiMail, FiLogOut } from "react-icons/fi";
import { useAuth } from "../context/AuthContext";
import logo from "../images/fnlogo.png";
import "./Navbar.css";

function Navbar({ hideHowItWorks = false }) {
  const [scrolled, setScrolled] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isDashboard = location.pathname === "/dashboard";

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToHowItWorks = () => {
    const section = document.getElementById("how-it-works");
    if (section) section.scrollIntoView({ behavior: "smooth" });
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className={`navbar${scrolled ? " navbar--scrolled" : ""}`}>
      <Link to="/">
        <img src={logo} alt="Logo" className="logo" />
      </Link>

      {!isDashboard && (
        <div className="menu">
          {!hideHowItWorks && (
            <a href="#" onClick={(e) => { e.preventDefault(); scrollToHowItWorks(); }}>
              <FiHelpCircle size={20} /> How it works
            </a>
          )}
          <Link to="/dashboard">
            <FiBarChart2 size={20} /> Dashboard
          </Link>
          <Link to="/contact">
            <FiMail size={20} /> Contact Us
          </Link>
        </div>
      )}

      <div className="actions">
        {user ? (
          <button onClick={handleLogout} className="signup" style={{ padding: "8px 24px" }}>
            <FiLogOut size={18} /> Logout
          </button>
        ) : (
          <>
            <Link to="/login">
              <FiLogIn size={20} /> Log in
            </Link>
            <Link to="/signup" className="signup">
              <FiUserPlus size={20} /> Sign up
            </Link>
          </>
        )}
      </div>
    </div>
  );
}

export default Navbar;