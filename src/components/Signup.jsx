import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FiUser, FiMail, FiLock, FiArrowLeft } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';
import heroBg from '../images/HeroSection.png';
import './Auth.css';

function Signup() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const { signup } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    try {
      await signup(fullName, email, password, confirmPassword);
    } catch (err) {
      setError(err.response?.data?.msg || 'Signup failed');
    }
  };

  return (
    <div className="auth-fullscreen">
      <div className="auth-blur-background" style={{ backgroundImage: `url(${heroBg})` }}></div>
      <div className="auth-back">
        <Link to="/"><FiArrowLeft size={18} /> Back to Home</Link>
      </div>
      <div className="auth-card">
        <h2>Create Account</h2>
        {error && <p style={{ color: '#ff6b6b', textAlign: 'center' }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <FiUser className="input-icon" />
            <input type="text" placeholder="Full Name" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          </div>
          <div className="input-group">
            <FiMail className="input-icon" />
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="input-group">
            <FiLock className="input-icon" />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <div className="input-group">
            <FiLock className="input-icon" />
            <input type="password" placeholder="Confirm Password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
          </div>
          <button type="submit">Sign Up</button>
        </form>
        <p>Already have an account? <Link to="/login">Log in</Link></p>
      </div>
    </div>
  );
}

export default Signup;