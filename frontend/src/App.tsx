import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Questionnaire from './pages/Questionnaire/Questionnaire'
import GymsPage from './pages/GymsPage/GymsPage'
import './App.css'
import Navbar from './pages/Navbar/Navbar';

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/questionnaire" element={<Questionnaire />} />
        <Route path="/gyms" element={<GymsPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
