import React, { useState } from 'react';
import axios from 'axios';

function BulkTagging() {
  const [urls, setUrls] = useState([{ value: '' }]);
  const [tags, setTags] = useState([{ value: '' }]);
  const [operation, setOperation] = useState(1); // 1 = add, 0 = remove
  const [message, setMessage] = useState('');

  const handleInputChange = (index, value, type) => {
    const list = type === 'url' ? [...urls] : [...tags];
    list[index].value = value;

    type === 'url' ? setUrls(list) : setTags(list);
  };

  const addField = (type) => {
    const list = type === 'url' ? [...urls] : [...tags];
    list.push({ value: '' });

    type === 'url' ? setUrls(list) : setTags(list);
  };

  const removeField = (index, type) => {
    const list = type === 'url' ? [...urls] : [...tags];
    if (list.length === 1) return; // Prevent removing the last field

    list.splice(index, 1);
    type === 'url' ? setUrls(list) : setTags(list);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const authorizationToken = sessionStorage.getItem('idToken');

    const urlArray = urls.map(u => u.value.trim()).filter(Boolean);
    const tagArray = tags.map(t => t.value.trim()).filter(Boolean);

    const payload = {
      urls: urlArray,
      operation,
      tags: tagArray,
    };

    console.log('Payload:', payload);

    try {
      const response = await axios.post('https://ynjaek8j7a.execute-api.us-east-1.amazonaws.com/dev/tag', payload, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authorizationToken, // Include the authorization token
        }
      });
      setMessage(`Success: ${response.data.message || 'Tags updated'}`);
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.message || error.message}`);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '600px', margin: 'auto' }}>
      <h2>Bulk Tagging</h2>
      <form onSubmit={handleSubmit}>

        {/* URL Fields */}
        <label>Image URLs:</label>
        {urls.map((url, index) => (
          <div key={index} style={{ display: 'flex', gap: '0.5rem', marginTop: '5px' }}>
            <input
              type="text"
              placeholder="https://example.com/image.png"
              value={url.value}
              onChange={(e) => handleInputChange(index, e.target.value, 'url')}
              style={{
                flex: 1,
                padding: '10px',
                borderRadius: '8px',
                border: '1px solid #ccc',
                width: '200px',
                fontSize: '1rem',
            }}
            />
            <button type="button" onClick={() => removeField(index, 'url')}>❌</button>
          </div>
        ))}
        <button type="button" onClick={() => addField('url')} style={{
            marginTop: '1.5rem',
            backgroundColor: '#2196F3',
            color: 'white',
            padding: '10px 16px',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '1rem',
      }}>
          + Add URL
        </button>

        <label style={{ marginTop: '1.5rem', display: 'block' }}>Tags (e.g., crow,1):</label>
        {tags.map((tag, index) => (
          <div key={index} style={{ display: 'flex', gap: '0.5rem', marginTop: '5px' }}>
            <input
              type="text"
              placeholder="e.g., crow,1"
              style={{
                flex: 1,
                padding: '10px',
                borderRadius: '8px',
                border: '1px solid #ccc',
                width: '200px',
                fontSize: '1rem',
            }}
              value={tag.value}
              onChange={(e) => handleInputChange(index, e.target.value, 'tag')}
            />
            <button type="button" onClick={() => removeField(index, 'tag')}>❌</button>
          </div>
        ))}
        <button type="button" onClick={() => addField('tag')} style={{
            marginTop: '1.5rem',
            backgroundColor: '#2196F3',
            color: 'white',
            padding: '10px 16px',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '1rem',
      }}>
          + Add Tag
        </button>

        {/* Operation Toggle */}
        <div style={{ marginTop: '1.5rem' }}>
          <label>
            <input
              type="radio"
              name="operation"
              value={1}
              checked={operation === 1}
              onChange={() => setOperation(1)}
            />
            Add Tags
          </label>
          <label style={{ marginLeft: '1rem' }}>
            <input
              type="radio"
              name="operation"
              value={0}
              checked={operation === 0}
              onChange={() => setOperation(0)}
            />
            Remove Tags
          </label>
        </div>

        {/* Submit */}
        <button type="submit" style={{
        marginTop: '1.5rem',
        backgroundColor: '#2196F3',
        color: 'white',
        padding: '10px 16px',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '1rem',
      }}>
          Submit
        </button>
      </form>

      {message && <p style={{ marginTop: '1rem' }}>{message}</p>}
    </div>
  );
}

export default BulkTagging;
