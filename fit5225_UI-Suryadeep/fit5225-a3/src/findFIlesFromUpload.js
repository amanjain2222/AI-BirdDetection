import React, { useState } from 'react';
import axios from 'axios';
import wavToBase64 from './toBase64Converter';
import birdsTable from './birdsTable';

function FindFilesFromUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false); 

  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (!file) return;
    
    const allowedTypes = ['mp3', 'wav', 'm4a', 'mp4', 'avi', 'mov' ,'jpg', 'png']
    
    const fileExtension = file.name.split('.').pop().toLowerCase();
    console.log(fileExtension);

    if (!allowedTypes.includes(fileExtension)) {
      alert('Only .mp3, .wav, .m4a, .mp4, .avi, .mov, .jpg and .png files are allowed for audio, video and images.'); 
      event.target.value = ''; // reset input
      return;
  }
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    const allowedImages = ['jpg', 'png']
    const allowedAudios = ['mp3', 'wav', 'm4a']
    const allowedVideos = ['mp4', 'avi', 'mov']
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (!file) {
      setMessage('Please select a file first.');
      return;
    }
    
    setIsLoading(true);

    const base64Data = await wavToBase64(file);

    try {
      // if file type is audio:
      if(allowedAudios.includes(fileExtension)){
        const process_url = 'https://ynjaek8j7a.execute-api.us-east-1.amazonaws.com/dev/search/byAudio';

        const response = await axios.post(process_url, 
            {
                audio: base64Data,
                filename: file.name
            }
            ,{
            headers: {
            'Content-Type': 'application/json'
            }
        });

        alert(`File has been processed successfully!`);
        console.log(response.data);

        const results = response.data.matching_media.map( result => result.MediaURL);

        const table = birdsTable(results);
        console.log(table);

        const container = document.getElementById('SimilarFilesContainer');
        container.innerHTML = '';
        container.appendChild(table);
        
      }

      else if(allowedImages.includes(fileExtension)){
        const process_url = 'https://ynjaek8j7a.execute-api.us-east-1.amazonaws.com/dev/search/byImage';

        const response = await axios.post(process_url, 
            {
                image: base64Data
            }
            ,{
            headers: {
            'Content-Type': 'application/json'
            }
        });

        alert(`File has been processed successfully!`);
        console.log(response);
        const results = response.data.results.map( result => result.MediaURL);

        const table = birdsTable(results);
        console.log(table);

        const container = document.getElementById('SimilarFilesContainer');
        container.innerHTML = '';
        container.appendChild(table);
        
      }
      else if(allowedVideos.includes(fileExtension)){
        const process_url = 'https://ynjaek8j7a.execute-api.us-east-1.amazonaws.com/dev/search/byVideo';

        const response = await axios.post(process_url, 
            {
                video: base64Data
            }
            ,{
            headers: {
            'Content-Type': 'application/json'
            }
        });

        alert(`File has been processed successfully!`);
        console.log(response);
        const results = response.data.results.map( result => result.MediaURL);

        const table = birdsTable(results);
        console.log(table);

        const container = document.getElementById('SimilarFilesContainer');
        container.innerHTML = '';
        container.appendChild(table);
      }

    } catch (error) {
      console.error('Processing failed:', error);
      alert('Processing failed: ' + (error.response?.data || error.message));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ 
  maxWidth: '500px',
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
  }}>Find Files based on Files you Upload</h2>
  
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
      {isLoading ? 'Searching...' : 'Search'}
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

export default FindFilesFromUpload;