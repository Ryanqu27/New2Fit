import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import api from '.././api';

const loginUser = async (google_token: string) => {
    const response = await api.post('/api/users/login', { google_token });
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
        auth.login(user);
        navigate('/questionnaire');
    }

    const handleError = () => {
        console.error('Google login failed');
    }

    return (
        <div>
            <h1>Welcome to New2Fit! Login to continue</h1>
            <GoogleLogin onSuccess={handleSuccess} onError={handleError} />
        </div>
    )
}