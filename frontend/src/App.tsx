import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Questionnaire from './Questionnaire'
import GymsPage from './GymsPage'
import './App.css'
import './Navbar.css'
import Navbar from './Navbar';

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
