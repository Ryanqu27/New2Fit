import { BrowserRouter, Routes, Route, Outlet, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import GymsPage from './pages/GymsPage/GymsPage'
import DashboardPage from './pages/DashboardPage/DashboardPage'
import AICamera from './pages/AICameraPage/AICamera'
import Workouts from './pages/WorkoutsPage/Workouts'
import './App.css'
import Navbar from './pages/Navbar/Navbar';
import ProtectedRoute from './Auth/ProtectedRoute';
import LoginPage from './Auth/LoginPage';
import RegisterPage from './Auth/RegisterPage';
import SetUsernamePage from './Auth/SetUsernamePage';
import { AuthProvider } from './Auth/AuthContext';
import { GoogleOAuthProvider } from '@react-oauth/google';
import SettingsPage from './pages/SettingsPage/SettingsPage';
import { SettingsProvider } from './Settings/SettingsContext';
import MessagesPage from './pages/MessagesPage/MessagesPage';
import ProfilePage from './pages/ProfilePage/ProfilePage';

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

// Listens for the custom 'unauthorized' event fired by the Axios interceptor
// in api.ts and navigates to /login using React Router (no hard page reload).
function AuthRedirectHandler() {
  const navigate = useNavigate();
  useEffect(() => {
    const handleUnauthorized = () => navigate('/login', { replace: true });
    window.addEventListener('unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, [navigate]);
  return null;
}

function App() {
  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthProvider>
        <BrowserRouter>
          <AuthRedirectHandler />
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/set-username" element={<SetUsernamePage />} />
            <Route element={
              <ProtectedRoute>
                <SettingsProvider>
                  <Navbar />
                  <Outlet />
                </SettingsProvider>
              </ProtectedRoute>
            }>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/gyms" element={<GymsPage />} />
              <Route path="/camera" element={<AICamera />} />
              <Route path="/workouts" element={<Workouts />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/messages" element={<MessagesPage />} />
              <Route path="/profile" element={<ProfilePage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </GoogleOAuthProvider>


  )
}

export default App
