import { useAuth } from '../../Auth/AuthContext';
import './HomePage.css';

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="home-container">
        <div className="home-content">
          <h1 className="home-title">
            Welcome <span className="home-name">{user.first_name}</span>
          </h1>
          <p className="home-subtitle">
            New2Fit helps introduce and guide you through your fitness journey.
          </p>
        </div>
    </div>
  );
}
