import { useState, useRef, useEffect } from 'react';
import { NavLink, Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../Auth/AuthContext";
import { getAvatarUrl } from "../../api";
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const avatarUrl = getAvatarUrl(user?.profile_picture_url);
  const initials = user?.first_name ? user.first_name.charAt(0).toUpperCase() : '?';

  return (
    <nav className="navbar">
      <div className="nav-links">
        {[
          { to: '/', label: 'Dashboard', end: true },
          { to: '/gyms', label: 'Find Gyms' },
          { to: '/camera', label: 'AI Camera' },
          { to: '/workouts', label: 'Workouts' },
          { to: '/messages', label: 'Messages' },
        ].map((route) => (
          <NavLink
            key={route.to}
            to={route.to}
            end={route.end}
            className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          >
            {route.label}
          </NavLink>
        ))}
      </div>

      <div className="nav-profile-container" ref={dropdownRef}>
        <button 
          className="nav-avatar-btn" 
          onClick={() => setDropdownOpen(!dropdownOpen)}
          aria-label="Toggle profile menu"
        >
          {avatarUrl ? (
            <img src={avatarUrl} alt="Profile" className="nav-avatar-img" />
          ) : (
            <div className="nav-avatar-initials">{initials}</div>
          )}
        </button>
        {dropdownOpen && (
          <div className="nav-dropdown">
            <Link to="/profile" className="nav-dropdown-item" onClick={() => setDropdownOpen(false)}>
              Profile
            </Link>
            <Link to="/settings" className="nav-dropdown-item" onClick={() => setDropdownOpen(false)}>
              Settings
            </Link>
            <div className="nav-dropdown-divider" />
            <button className="nav-dropdown-item logout-dropdown-item" onClick={handleLogout}>
              Log Out
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}