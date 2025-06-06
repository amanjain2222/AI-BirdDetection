// App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './navbar'; // you'll create this
import FileUpload from './fileUpload';
import SearchImage from './searchImage';
import About from './about';

function App() {
  return (
    <Router>
      <Navbar />
      <div style={{ padding: '2rem' }}>
        <Routes>
          <Route path="/" element={<FileUpload />} />
          <Route path="/search" element={<SearchImage />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
