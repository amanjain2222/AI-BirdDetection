// components/Navbar.js
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { signOut } from './authService';

const Navbar = () => {

    const navigate = useNavigate();
    const isLoggedIn = !!sessionStorage.getItem('idToken');

    const handleLogout = () => {
        signOut();
        navigate('/login');
    };


    return (
        <nav style={styles.nav}>
            <h2 style={styles.logo}>Monash Birdy Buddies</h2>
            <div style={styles.links}>
                {isLoggedIn && (
                <>
                    <Link to="/" style={styles.link}>Upload Files</Link>
                    <Link to="/search" style={styles.link}>Search Files</Link>
                    <Link to="/tagging" style={styles.link}>Tagging</Link>
                    <Link to="/delete" style={styles.link}>Delete Files</Link>
                    <Link to="/sns-topics" style={styles.link}>SNS Topics</Link>
                    <Link to="/about" style={styles.link}>About Us</Link>
                    <button onClick={handleLogout} style={styles.link}>Logout</button>
                </>
                )}
                {!isLoggedIn && (
                <Link to="/login" style={styles.link}>Login</Link>
                )}
            </div>
        </nav>
  );
};

const styles = {
    nav: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        backgroundColor: '#2a2a2a',
        color: 'white',
    },
    logo: {
        margin: 0,
    },
    links: {
        display: 'flex',
        gap: '1rem',
    },
    link: {
        color: 'white',
        textDecoration: 'none',
        fontWeight: 'bold',
        backgroundColor: '#2a2a2a',
        border: 'none'
    }
};

export default Navbar;