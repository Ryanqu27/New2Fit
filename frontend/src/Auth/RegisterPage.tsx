import { useState } from 'react';
import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from './AuthContext';
import api from '.././api';
import './LoginPage.css';

const loginWithGoogle = async (google_token: string) => {
    const response = await api.post('/users/login', { google_token });
    return response.data;
}

export default function RegisterPage() {
    const navigate = useNavigate();
    const auth = useAuth();
    
    const [firstName, setFirstName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
        const token = credentialResponse.credential;
        if (!token) return;
        
        try {
            setError('');
            const user = await loginWithGoogle(token);
            auth.login(user);
            navigate('/');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Google sign up failed');
        }
    }

    const handleGoogleError = () => {
        setError('Google sign up failed');
    }

    const handleRegisterSubmit = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const response = await api.post('/users/register', { 
                first_name: firstName, 
                email, 
                password 
            });
            auth.login(response.data);
            navigate('/');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create account');
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="login-page-container">
            <div className="login-bg-glow"></div>
            <div className="login-bg-glow-2"></div>
            
            <div className="login-card">
                <div className="login-header">
                    <p className="login-welcome">Join us today</p>
                    <h1 className="login-brand">
                        <span className="login-brand-name">New2Fit</span>
                    </h1>
                    <p className="login-subtitle">
                        Create an account to start your journey
                    </p>
                </div>

                {error && <div className="login-error">{error}</div>}

                <form className="email-login-form" onSubmit={handleRegisterSubmit}>
                    <div className="input-group">
                        <input 
                            type="text" 
                            placeholder="First Name" 
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            required 
                        />
                    </div>
                    <div className="input-group">
                        <input 
                            type="email" 
                            placeholder="Email address" 
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required 
                        />
                    </div>
                    <div className="input-group">
                        <input 
                            type="password" 
                            placeholder="Password" 
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required 
                            minLength={6}
                        />
                    </div>
                    <button type="submit" className="email-login-btn" disabled={isLoading}>
                        {isLoading ? 'Creating account...' : 'Create Account'}
                    </button>
                </form>

                <div className="login-divider">
                    <span>or continue with</span>
                </div>

                <div className="login-btn-wrapper">
                    <GoogleLogin 
                        onSuccess={handleGoogleSuccess} 
                        onError={handleGoogleError} 
                        theme="outline"
                        shape="pill"
                        size="large"
                        text="signup_with"
                    />
                </div>

                <div className="auth-switch-link">
                    Already have an account? <Link to="/login">Log in</Link>
                </div>
            </div>
        </div>
    );
}
