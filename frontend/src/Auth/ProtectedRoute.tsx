import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const auth = useAuth();
    if (!auth.user) {
        return <Navigate to="/login" />
    }
    
    if (!auth.user.username) {
        return <Navigate to="/set-username" />
    }

    return children;
}