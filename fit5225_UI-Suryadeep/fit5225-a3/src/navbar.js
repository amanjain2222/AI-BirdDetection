// components/Navbar.js
import React from 'react';
import { Link } from 'react-router-dom'; // if you're using React Router

const Navbar = () => {
    return (
        <nav style={styles.nav}>
            <h2 style={styles.logo}>Monash Birdy Buddies</h2>
            <div style={styles.links}>
                <Link to="/" style={styles.link}>Upload Files</Link>
                <Link to="/search" style={styles.link}>Search Files</Link>
                <Link to="/about" style={styles.link}>About Us</Link>
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
    }
};

export default Navbar;