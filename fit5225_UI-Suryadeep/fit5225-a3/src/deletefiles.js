import React, { useState } from 'react';
import axios from 'axios';

function DeleteFiles() {
  const [urls, setUrls] = useState([{ value: '' }]);
  const [message, setMessage] = useState('');

  const handleInputChange = (index, value) => {
    const updated = [...urls];
    updated[index].value = value;
    setUrls(updated);
  };

  const addUrlField = () => {
    setUrls([...urls, { value: '' }]);
  };

  const removeUrlField = (index) => {
    if (urls.length === 1) return; // Always keep at least one
    const updated = [...urls];
    updated.splice(index, 1);
    setUrls(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const urlList = urls.map(u => u.value.trim()).filter(Boolean);

    if (urlList.length === 0) {
      setMessage('Please provide at least one valid URL.');
      return;
    }

    console.log('URLs to delete:', urlList);

    try {
      const response = await axios.delete('https://ynjaek8j7a.execute-api.us-east-1.amazonaws.com/dev/media', {
        data: {
        urls: urlList
      },
        headers: {
          'Content-Type': 'application/json'
        }
      });

      setMessage(`${response.data.message || 'Files deleted successfully.'}`);
      setUrls([{ value: '' }]);
    } catch (error) {
      setMessage(`${error.response?.data?.message || error.message}`);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '600px', margin: 'auto' }}>
      <h2>Delete Files</h2>
      <form onSubmit={handleSubmit}>
        <label>Enter S3 URLs to delete:</label>
        {urls.map((u, index) => (
          <div key={index} style={{ display: 'flex', gap: '0.5rem', marginTop: '5px' }}>
            <input
              type="text"
              placeholder="https://your-bucket.s3.amazonaws.com/image.jpg"
              style={{ width: '100%', marginTop: '5px',  padding: '10px',
                borderRadius: '8px',
                border: '1px solid #ccc',
                fontSize: '1rem'}}
              value={u.value}
              onChange={(e) => handleInputChange(index, e.target.value)}
            />
            <button type="button" onClick={() => removeUrlField(index)}>❌</button>
          </div>
        ))}

        <button type="button" onClick={addUrlField} style={{
            marginTop: '1.5rem',
            backgroundColor: '#2196F3',
            color: 'white',
            padding: '10px 16px',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '1rem',
      }}>+ Add URL</button>
        <br />
        <button type="submit" style={{
            marginTop: '1.5rem',
            backgroundColor: '#2196F3',
            color: 'white',
            padding: '10px 16px',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '1rem',
      }}>Delete</button>
      </form>

      {message && <p style={{ marginTop: '1rem' }}>{message}</p>}
    </div>
  );
}

export default DeleteFiles;