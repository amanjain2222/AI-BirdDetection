import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './navbar';
import FileUpload from './fileUpload';
import SearchImage from './searchImage';
import About from './about';
import Login from './login';
import PrivateRoute from './privateRoute';
import Signup from './signup';
import ConfirmSignup from './confirmSignUp';
import BulkTagging from './bulktagging';
import DeleteFiles from './deletefiles';


function App() {
  return (
    <Router>
      <Navbar />
      <div style={{ padding: '2rem' }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/confirm" element={<ConfirmSignup />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <FileUpload />
              </PrivateRoute>
            }
          />
          <Route
            path="/search"
            element={
              <PrivateRoute>
                <SearchImage />
              </PrivateRoute>
            }
          />
          <Route
            path="/tagging"
            element={
              <PrivateRoute>
                <BulkTagging />
              </PrivateRoute>
            }
          />
          <Route
            path="/delete"
            element={
              <PrivateRoute>
                <DeleteFiles />
              </PrivateRoute>
            }
          />
          <Route
            path="/about"
            element={
              <PrivateRoute>
                <About />
              </PrivateRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;