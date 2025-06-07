import React, { useState } from 'react';
import axios from 'axios';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false); 

  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (!file) return;
    
    const allowedTypes = ['mp3', 'mp4', 'wav', 'jpg']
    const fileExtension = file.name.split('.').pop().toLowerCase();
    console.log(fileExtension);

    if (!allowedTypes.includes(fileExtension)) {
      alert('Only .mp3, .mp4, .wav, and .jpg files are allowed.');
      event.target.value = ''; // reset input
      return;
  }
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file first.');
      return;
    }
    
    setIsLoading(true);

    try {
      // Step 1: Get pre-signed URL from your Lambda backend
      const presignRes = await axios.post('https://qiorooauyl.execute-api.us-east-1.amazonaws.com/dev/upload', {
        file_name: file.name,
        content_type: file.type
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const { upload_url, s3_key } = presignRes.data;


      // Step 2: Upload the file directly to S3
      await axios.put(upload_url, file, {
        headers: {
          'Content-Type': file.type
        }
      });

      alert(`File uploaded to S3 successfully!\nS3 Key: ${s3_key}`);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed: ' + (error.response?.data || error.message));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ 
  maxWidth: '500px',
  margin: '2rem auto',
  padding: '2rem',
  backgroundColor: '#2a2a2a',
  borderRadius: '12px',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
  color: '#f0f0f0'
}}>
  <h2 style={{
    marginBottom: '1.5rem',
    color: '#ffffff',
    fontWeight: '600',
    fontSize: '1.5rem',
    textAlign: 'center'
  }}>Upload a File</h2>
  
  <div style={{
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem'
  }}>
    <label style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '0.5rem'
    }}>
      <span style={{
        fontSize: '0.9rem',
        color: '#cccccc'
      }}>Select your file</span>
      <input 
        type="file" 
        onChange={handleFileChange}
        style={{
          padding: '0.75rem',
          border: '1px solid #444',
          borderRadius: '6px',
          backgroundColor: '#333333',
          color: '#ffffff',
          cursor: 'pointer',
          transition: 'border-color 0.2s',
          ':hover': {
            borderColor: '#555'
          }
        }}
      />
    </label>
    
        <button 
      onClick={handleUpload}
      disabled={isLoading}
      style={{
        padding: '0.75rem 1.5rem',
        backgroundColor: isLoading ? '#666' : '#4f46e5',
        color: 'white',
        border: 'none',
        borderRadius: '6px',
        fontWeight: '500',
        cursor: isLoading ? 'not-allowed' : 'pointer',
        transition: 'background-color 0.2s',
        marginTop: '0.5rem'
      }}
    >
      {isLoading ? 'Uploading...' : 'Upload'}
    </button>

    {isLoading && (
      <div style={{ 
        marginTop: '1rem', 
        textAlign: 'center', 
        color: '#cccccc', 
        fontStyle: 'italic' 
      }}>
        Loading...
      </div>
    )}


    
    {message && (
      <p style={{
        marginTop: '1rem',
        padding: '0.75rem',
        borderRadius: '6px',
        backgroundColor: message.includes('success') ? '#1a3a1a' : '#3a1a1a',
        color: message.includes('success') ? '#a0f0a0' : '#f0a0a0'
      }}>
        {message}
      </p>
    )}
  </div>
</div>
  );
}

export default FileUpload;