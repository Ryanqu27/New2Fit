import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import api from '.././api';
import './LoginPage.css';

const loginUser = async (google_token: string) => {
    const response = await api.post('/users/login', { google_token });
    return response.data;
}

export default function LoginPage() {
    const navigate = useNavigate();
    const auth = useAuth();
    
    // When user successfully signs in with Google
    const handleSuccess = async (credentialResponse: CredentialResponse) => {
        const token = credentialResponse.credential;
        if (!token) {
            return;
        }
        const user = await loginUser(token);
        auth.login(user, token);
        navigate('/');
    }

    const handleError = () => {
        console.error('Google login failed');
    }

    return (
        <div className="login-page-container">
            <div className="login-bg-glow"></div>
            <div className="login-bg-glow-2"></div>
            
            <div className="login-card">
                <div className="login-header">
                    <p className="login-welcome">Welcome to</p>
                    <h1 className="login-brand">
                        <span className="login-brand-name">New2Fit</span>
                    </h1>
                    <p className="login-subtitle">
                        Sign in to start your fitness journey
                    </p>
                </div>

                <div className="login-btn-wrapper">
                    <GoogleLogin 
                        onSuccess={handleSuccess} 
                        onError={handleError} 
                        theme="outline"
                        shape="pill"
                        size="large"
                    />
                </div>
            </div>
        </div>
    );
}
