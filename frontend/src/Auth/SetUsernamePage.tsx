import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import api from '../api';
import './LoginPage.css';

export default function SetUsernamePage() {
    const navigate = useNavigate();
    const { user, login } = useAuth();
    
    const [username, setUsername] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    useEffect(() => {
        if (!user) {
            navigate('/login');
        } else if (user.username) {
            navigate('/');
        }
    }, [user, navigate]);

    const handleSubmit = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const response = await api.patch('/users/me/username', { username });
            // Update the user in context with the returned user object (which now has a username)
            login(response.data);
            navigate('/');
        } catch (err) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail || 'Failed to set username');
            } else {
                setError('Failed to set username');
            }
        } finally {
            setIsLoading(false);
        }
    }

    if (!user) return null;

    return (
        <div className="login-page-container">
            <div className="login-bg-glow"></div>
            <div className="login-bg-glow-2"></div>
            
            <div className="login-card">
                <div className="login-header">
                    <p className="login-welcome">Almost there!</p>
                    <h1 className="login-brand">
                        <span className="login-brand-name">New2Fit</span>
                    </h1>
                    <p className="login-subtitle">
                        Choose a unique username to continue
                    </p>
                </div>

                {error && <div className="login-error">{error}</div>}

                <form className="email-login-form" onSubmit={handleSubmit}>
                    <div className="input-group">
                        <input 
                            type="text" 
                            placeholder="Username" 
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required 
                            minLength={3}
                            maxLength={30}
                        />
                    </div>
                    
                    <button type="submit" className="email-login-btn" disabled={isLoading}>
                        {isLoading ? 'Saving...' : 'Complete Profile'}
                    </button>
                </form>
            </div>
        </div>
    );
}
