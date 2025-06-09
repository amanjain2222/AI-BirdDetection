import React, { useState } from 'react';
import axios from 'axios';

function ThumbnailSearch() {
  const [thumbnailURL, setThumbnailURL] = useState('');
  const [fullImageURL, setFullImageURL] = useState('');
  const [message, setMessage] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!thumbnailURL.trim()) {
      setMessage("Please enter a thumbnail URL.");
      return;
    }

    try {
      const response = await axios.post('https://ktchxqkala.execute-api.us-east-1.amazonaws.com/dev/search/thumbnail', {
        thumbnail: thumbnailURL.trim(),
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log(response.data);

      setFullImageURL(response.data.results.MediaURL);
      setMessage('');
    } catch (error) {
      //setMessage(`Error: ${error.response?.data?.message || error.message}`);
      //setFullImageURL('');
    }
  };

  return (
    <div style={{ maxWidth: '600px'}}>
      <h2>Find Full Image by Thumbnail URL</h2>
      <form onSubmit={handleSearch}>
        <label>Enter Thumbnail S3 URL:</label>
        <input
          type="text"
          placeholder="https://bucket.s3.amazonaws.com/image-thumb.png"
          value={thumbnailURL}
          onChange={(e) => setThumbnailURL(e.target.value)}
          style={{ width: '100%', marginTop: '5px',  padding: '10px',
            borderRadius: '8px',
            border: '1px solid #ccc',
            fontSize: '1rem',  }}
        />

        <button type="submit" style={{
        backgroundColor: '#2196F3',
        color: 'white',
        padding: '10px 16px',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '1rem',
        marginTop: '1rem',
      }}>
          Search
        </button>
      </form>

      {message && <p style={{ marginTop: '1rem' }}>{message}</p>}

      {fullImageURL && (
        <div style={{ marginTop: '1rem' }}>
          <strong>Full Image URL:</strong>
          <p><a href={fullImageURL} target="_blank" rel="noopener noreferrer">{fullImageURL}</a></p>
          <img src={fullImageURL} alt="Full Size" style={{ maxWidth: '100%', marginTop: '10px' }} />
        </div>
      )}
    </div>
  );
}

export default ThumbnailSearch;