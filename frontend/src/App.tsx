import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom'
import Questionnaire from './pages/QuestionnairePage/Questionnaire'
import GymsPage from './pages/GymsPage/GymsPage'
import DashboardPage from './pages/DashboardPage/DashboardPage'
import AICamera from './pages/AICameraPage/AICamera'
import Workouts from './pages/WorkoutsPage/Workouts'
import './App.css'
import Navbar from './pages/Navbar/Navbar';
import ProtectedRoute from './Auth/ProtectedRoute';
import LoginPage from './Auth/LoginPage';
import RegisterPage from './Auth/RegisterPage';
import { AuthProvider } from './Auth/AuthContext';
import { GoogleOAuthProvider } from '@react-oauth/google';
import SettingsPage from './pages/SettingsPage/SettingsPage';
import { SettingsProvider } from './Settings/SettingsContext';

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
function App() {
  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route element={
              <ProtectedRoute>
                <SettingsProvider>
                  <Navbar />
                  <Outlet />
                </SettingsProvider>
              </ProtectedRoute>
            }>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/questionnaire" element={<Questionnaire />} />
              <Route path="/gyms" element={<GymsPage />} />
              <Route path="/camera" element={<AICamera />} />
              <Route path="/workouts" element={<Workouts />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </GoogleOAuthProvider>


  )
}

export default App
