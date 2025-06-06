function About() {
    return (
        <div style={{
            maxWidth: '800px',
            margin: '2rem auto',
            padding: '3rem',
            backgroundColor: 'rgba(30, 30, 30, 0.8)',
            borderRadius: '16px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            color: '#f0f0f0',
            textAlign: 'center',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            backgroundImage: 'linear-gradient(to bottom right, rgba(40, 40, 40, 0.8), rgba(25, 25, 25, 0.9))'
        }}>
            <h1 style={{
                fontSize: '2.5rem',
                fontWeight: '600',
                marginBottom: '1.5rem',
                background: 'linear-gradient(90deg, #6ee7b7, #3b82f6)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                letterSpacing: '0.5px'
            }}>
                About Our Team
            </h1>
            
            <p style={{
                fontSize: '1.2rem',
                lineHeight: '1.8',
                marginBottom: '2rem',
                opacity: '0.9'
            }}>
                We are a dedicated team working on <strong>Unit 5225 Project 3</strong>, 
                committed to delivering exceptional results for this assignment.
            </p>
            
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '2rem',
                marginTop: '2rem',
                flexWrap: 'wrap'
            }}>
                <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    padding: '1.5rem',
                    borderRadius: '12px',
                    minWidth: '200px',
                    border: '1px solid rgba(255, 255, 255, 0.05)'
                }}>
                    <h3 style={{ color: '#6ee7b7', marginBottom: '0.5rem' }}>Our Mission</h3>
                    <p>Understand AWS based solutions </p>
                </div>
                
                <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    padding: '1.5rem',
                    borderRadius: '12px',
                    minWidth: '200px',
                    border: '1px solid rgba(255, 255, 255, 0.05)'
                }}>
                    <h3 style={{ color: '#3b82f6', marginBottom: '0.5rem' }}>Our Values</h3>
                    <p>Collaboration • Quality • Innovation</p>
                </div>
            </div>
        </div>
    );
}

export default About;