import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiMail, FiLock, FiArrowLeft } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';
import heroBg from '../images/HeroSection.png';
import './Auth.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.msg || 'Login failed');
    }
  };

  return (
    <div className="auth-fullscreen">
      <div className="auth-blur-background" style={{ backgroundImage: `url(${heroBg})` }}></div>
      <div className="auth-back">
        <Link to="/"><FiArrowLeft size={18} /> Back to Home</Link>
      </div>
      <div className="auth-card">
        <h2>Welcome Back</h2>
        {error && <p style={{ color: '#ff6b6b', textAlign: 'center' }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <FiMail className="input-icon" />
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="input-group">
            <FiLock className="input-icon" />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit">Log In</button>
        </form>
        <p>Don't have an account? <Link to="/signup">Sign up</Link></p>
      </div>
    </div>
  );
}

export default Login;