import React, { useState } from 'react';
import axios from 'axios';
import birdsTable from './birdsTable'

function SearchImage() {
    const [formData, setFormData] = useState([
        { birdName: '', birdCount: 0 }
    ]);

    const getRequest = async (event) => {
        event.preventDefault(); 

        const query_params = formData.filter(entry => entry.birdName != '').map(entry => entry.birdName + '=' + entry.birdCount).join('&');
        const preped_query = 'https://ktchxqkala.execute-api.us-east-1.amazonaws.com/dev/search?' + query_params;
        console.log(preped_query);

        
        axios.get(preped_query)
            .then(response => {
                console.log(response.data.results);
                const thumbnail_url = response.data.results.map(result => result.ThumbnailURL);
                const table = birdsTable(thumbnail_url);

                const container = document.getElementById('thumbnailurlContainer');
                container.innerHTML = '';
                container.appendChild(table);
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
    View Files Based on the Tags you Provide
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
    </div>
    );
}

export default SearchImage;