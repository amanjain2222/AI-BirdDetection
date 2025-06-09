import React, { useEffect, useState } from 'react';
import axios from 'axios';

function SNSTopicSelector() {
    const [topics, setTopics] = useState([]);
    const [selectedTopic, setSelectedTopic] = useState('');
    const [message, setMessage] = useState('');
    const [userEmail, setUserEmail] = useState('');

    // Fetch available SNS topics
    useEffect(() => {
        const fetchTopics = async () => {
            try {
                const response = await axios.get('https://ynjaek8j7a.execute-api.us-east-1.amazonaws.com/dev/sns');
                console.log('Fetched topics:', response);
                setTopics(response.data);
            } catch (err) {
                console.error('Error fetching topics:', err);
                setMessage('Failed to load topics');
            }
        };

        fetchTopics();
    }, []);

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!selectedTopic) {
            setMessage('Please select a topic.');
            return;
        }

        try {
            console.log('Submitting topic:', selectedTopic);
            console.log('User email:', userEmail);
            const response = await axios.post('https://ynjaek8j7a.execute-api.us-east-1.amazonaws.com/dev/sns',
                {
                    topicArn: selectedTopic,
                    email: userEmail
                }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            setMessage(`Success: ${response.data.message || 'Topic submitted successfully'}`);

        // Reset form and message after 3 seconds
        setTimeout(() => {
            setSelectedTopic('');
            setUserEmail('');
            setMessage('');
            // Optional: refresh topics again
            // fetchTopics();  // Make sure to define it outside useEffect
        }, 3000);
        } catch (error) {
            setMessage(`Error: ${error.response?.data?.message || error.message}`);

        // Auto-clear error after 5 seconds
        setTimeout(() => {
            setMessage('');
        }, 5000);
        }
    };

    return (
        <div style={{ padding: '2rem', maxWidth: '600px', margin: 'auto' }}>
            <h2>Select an SNS Topic</h2>

            <form onSubmit={handleSubmit}>
                <label htmlFor="email">Email Address:</label>
                <input
                    id="email"
                    type="email"
                    value={userEmail}
                    onChange={(e) => setUserEmail(e.target.value)}
                    placeholder="e.g., user@example.com"
                    style={{
                        padding: '0.5rem',
                        fontSize: '1rem',
                        width: '100%',
                        marginBottom: '1rem',
                        borderRadius: '6px',
                        border: '1px solid #ccc'
                    }}
                    required
                />
                <label htmlFor="topic">Select Topic:</label>
                <select
                    value={selectedTopic}
                    onChange={(e) => setSelectedTopic(e.target.value)}
                    style={{ padding: '0.5rem', fontSize: '1rem', width: '100%', marginBottom: '1rem' }}
                >
                    <option value="">-- Select a topic --</option>
                    {topics.map((item, index) => (
                        <option key={index} value={item.TopicArn}>
                            {item.TopicArn}
                        </option>
                    ))}
                </select>

                <button
                    type="submit"
                    style={{
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        padding: '10px 16px',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '1rem'
                    }}
                >
                    Submit
                </button>
            </form>

            {message && <p style={{ marginTop: '1rem' }}>{message}</p>}
        </div>
    );
}

export default SNSTopicSelector;
