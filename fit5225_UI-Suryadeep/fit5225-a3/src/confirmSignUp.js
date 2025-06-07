import React, { useState } from 'react';
import { confirmSignUp } from './authService';
import { useNavigate } from 'react-router-dom';

const ConfirmSignup = () => {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const navigate = useNavigate();

  const handleConfirm = async () => {
    try {
      await confirmSignUp(email, code);
      alert('Account confirmed! You can now log in.');
      navigate('/login');
    } catch (err) {
      alert('Confirmation failed. Make sure the code is correct.');
      console.log(err);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Confirm Your Signup</h2>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={e => setEmail(e.target.value)}
      /><br />
      <input
        type="text"
        placeholder="Verification Code"
        value={code}
        onChange={e => setCode(e.target.value)}
      /><br />
      <button onClick={handleConfirm}>Verify</button>
    </div>
  );
};

export default ConfirmSignup;