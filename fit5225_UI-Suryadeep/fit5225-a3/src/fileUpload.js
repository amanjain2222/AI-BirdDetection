import React, { useState } from 'react';
import axios from 'axios';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (!file) return;
    
    const allowedTypes = ['mp4', 'wav', 'jpg']
    const fileExtension = file.name.split('.').pop().toLowerCase();
    console.log(fileExtension);

    if (!allowedTypes.includes(fileExtension)) {
      alert('Only .mp4, .wav, and .jpg files are allowed.');
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

      setMessage(`File uploaded to S3 successfully!\nS3 Key: ${s3_key}`);
    } catch (error) {
      console.error('Upload failed:', error);
      setMessage('Upload failed: ' + (error.response?.data || error.message));
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Upload a File</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} style={{ marginTop: '1rem' }}>Upload</button>
      <p>{message}</p>
    </div>
  );
}

export default FileUpload;