import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom'
import Questionnaire from './pages/QuestionnairePage/Questionnaire'
import GymsPage from './pages/GymsPage/GymsPage'
import HomePage from './pages/HomePage/HomePage'
import AICamera from './pages/AICameraPage/AICamera'
import Workouts from './pages/WorkoutsPage/Workouts'
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
            <Route path="/login" element={<LoginPage />} />
            <Route element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <Outlet />
                </>
              </ProtectedRoute>
            }>
              <Route path="/" element={<HomePage />} />
              <Route path="/questionnaire" element={<Questionnaire />} />
              <Route path="/gyms" element={<GymsPage />} />
              <Route path="/camera" element={<AICamera />} />
              <Route path="/workouts" element={<Workouts />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </GoogleOAuthProvider>
    
    
  )
}

export default App
