// Signup.js
import React, { useState } from 'react';
import { signUp } from './authService';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSignup = async () => {
    try {
      await signUp(email, password);
      alert('Sign-up successful! Please check your email to confirm your account.');
      navigate('/confirm', { state: { email } });
    } catch (err) {
      alert('Sign-up failed!');
      console.log(err);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Sign Up</h2>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={e => setEmail(e.target.value)}
      /><br />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
      /><br />
      <button onClick={handleSignup}>Sign Up</button>
      <p>
        Already signed up but need to verify? <a href="/confirm">Click here</a>
      </p>
    </div>
  );
};

export default Signup;