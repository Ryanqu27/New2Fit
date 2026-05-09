import { BrowserRouter, Routes, Route, Outlet, Navigate } from 'react-router-dom'
import Questionnaire from './pages/Questionnaire/Questionnaire'
import GymsPage from './pages/GymsPage/GymsPage'
import './App.css'
import Navbar from './pages/Navbar/Navbar';
import ProtectedRoute from './Auth/ProtectedRoute';
import LoginPage from './Auth/LoginPage';
import { AuthProvider } from './Auth/AuthContext';
import { GoogleOAuthProvider } from '@react-oauth/google';

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
function App() {
  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <Outlet />
                </>
              </ProtectedRoute>
            }>
              <Route path="/questionnaire" element={<Questionnaire />} />
              <Route path="/gyms" element={<GymsPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </GoogleOAuthProvider>
    
    
  )
}

export default App
