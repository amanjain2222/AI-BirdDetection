// ./login.js
import React, { useState } from 'react';
import { signIn } from './authService';
import { Link, useNavigate } from 'react-router-dom';
import Signup from './signup';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      await signIn(email, password);
      navigate('/');
    } catch (err) {
      alert('Login failed!');
      console.log(err);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Login</h2>
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" /><br />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" /><br />
      <button onClick={handleLogin}>Sign In</button>
      <p>
        Don’t have an account? <Link to="/signup">Sign up here</Link>
      </p>
    </div>
  );
};

export default Login;