import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../Auth/AuthContext";
import './Navbar.css';

export default function Navbar() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="nav-links">
        <NavLink
          to="/"
          className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          end
        >
          Home
        </NavLink>
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
      </div>

      <button className="logout-btn" onClick={handleLogout}>
        Log Out
      </button>
    </nav>
  )
}