import React, { useState } from 'react';
import axios from 'axios';
import birdsTable from './birdsTable'
import FindFilesFromUpload from './findFIlesFromUpload';


function SearchImage() {
    const [formData, setFormData] = useState([
        { birdName: '', birdCount: 0 }
    ]);

    const getRequest = async (event) => {
        event.preventDefault(); 

        const query_params = formData.filter(entry => entry.birdName.trim() !== '').map(entry => `${encodeURIComponent(entry.birdName.trim())}=${encodeURIComponent(entry.birdCount !== '' ? entry.birdCount : 0)}`).join('&');
        const preped_query = 'https://t6yu3oclhk.execute-api.us-east-1.amazonaws.com/prod/search?' + query_params;

        const container = document.getElementById('thumbnailurlContainer');
    
        // Show loading spinner
        container.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>generating S3 Thumbnail URLs...</p>
            </div>
        `;

        console.log(preped_query);
        
        axios.get(preped_query)
          .then(response => {
            const results = response.data.results;
            console.log(response.data.results);

            if (Array.isArray(results) && results.length > 0) {
            // Extract URLs and file types
            const urlList = results.map(result => {
              if (result.FileType === "image") {
                return result.ThumbnailURL;
              } else {
                return result.MediaURL;
              }
            });
            // TODO: 
            const table = birdsTable(urlList);

            const container = document.getElementById('thumbnailurlContainer');
            container.innerHTML = '';
            container.appendChild(table);
          } else {
            const container = document.getElementById('thumbnailurlContainer');
            container.innerHTML = '<p>No results found.</p>';
          }
        });
    };

    const handleChange = (index, event) => {
        const { name, value } = event.target;
        const updatedFormData = [...formData];
        updatedFormData[index][name] = value;
        setFormData(updatedFormData);
    };

    const handleAddRow = () => {
        setFormData([...formData, { birdName: '', birdCount: 0 }]);
    };

    return (
        <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
  <h2 style={{ marginBottom: '1.5rem' }}>
    View Files Based on Bird Species
  </h2>
  <form onSubmit={getRequest}>
    {formData.map((entry, index) => (
      <div key={index} style={{ marginBottom: '1rem', display: 'flex', gap: '1rem' }}>
        <input
          type="text"
          name="birdName"
          placeholder="Input bird name"
          onChange={(e) => handleChange(index, e)}
          value={entry.birdName}
          style={{
            padding: '10px',
            borderRadius: '8px',
            border: '1px solid #ccc',
            width: '200px',
            fontSize: '1rem',
          }}
        />
        <input
          type="number"
          name="birdCount"
          min="0"
          placeholder="Max birds you want to see"
          onChange={(e) => handleChange(index, e)}
          value={entry.birdCount}
          style={{
            padding: '10px',
            borderRadius: '8px',
            border: '1px solid #ccc',
            width: '200px',
            fontSize: '1rem',
          }}
        />
      </div>
    ))}

    <button
      type="button"
      onClick={handleAddRow}
      style={{
        backgroundColor: '#4CAF50',
        color: 'white',
        padding: '10px 16px',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        marginBottom: '1rem',
        fontSize: '1rem',
      }}
    >
      Add Bird
    </button>
    <br />
    <button
      type="submit"
      style={{
        backgroundColor: '#2196F3',
        color: 'white',
        padding: '10px 16px',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '1rem',
      }}
    >
      Submit
    </button>
  </form>
        <div id="thumbnailurlContainer" style={{ marginTop: '2rem' }}></div>
        <div>
          <FindFilesFromUpload/>
        </div>
        <div id="SimilarFilesContainer" style={{ marginTop: '2rem' }}>
        </div>
    
  </div>
    );
}

export default SearchImage;