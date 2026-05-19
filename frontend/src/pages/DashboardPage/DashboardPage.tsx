import { useEffect, useState } from 'react';
import { useAuth } from '../../Auth/AuthContext';
import { getUserStats, type UserStatsResponse } from './DashboardService';
import './DashboardPage.css';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getUserStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch user stats", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="home-container">
      <div className="home-content">
        <h1 className="home-title">
          Welcome <span className="home-name">{user.first_name}</span>
        </h1>
        <p className="home-subtitle">
          Here is your fitness progress. Keep up the great work!
        </p>

        {loading ? (
          <div className="loading-stats">Loading your progress...</div>
        ) : (
          stats && (
            <div className="dashboard-grid">
              <div className="dashboard-section">
                <h2 className="section-title">This Week</h2>
                <div className="stats-cards">
                  <div className="stat-card">
                    <div className="stat-info">
                      <span className="stat-value">{stats.this_week_workouts}</span>
                      <span className="stat-label">Workouts</span>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-info">
                      <span className="stat-value">{stats.this_week_minutes}</span>
                      <span className="stat-label">Minutes</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="dashboard-section">
                <h2 className="section-title">All-Time</h2>
                <div className="stats-cards">
                  <div className="stat-card outline">
                    <div className="stat-info">
                      <span className="stat-value">{stats.all_time_workouts}</span>
                      <span className="stat-label">Workouts</span>
                    </div>
                  </div>
                  <div className="stat-card outline">
                    <div className="stat-info">
                      <span className="stat-value">{stats.all_time_minutes}</span>
                      <span className="stat-label">Minutes</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}
