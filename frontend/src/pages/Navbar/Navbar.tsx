import { NavLink } from "react-router-dom";
import './Navbar.css';

export default function Navbar() {
  return (
    <nav className="navbar">
      <NavLink 
        to="/questionnaire" 
        className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
      >
        Questionnaire & Plan
      </NavLink>
      <NavLink 
        to="/gyms" 
        className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
      >
        Find Gyms
      </NavLink>
    </nav>
  )
}