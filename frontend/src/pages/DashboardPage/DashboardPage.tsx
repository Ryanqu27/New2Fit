import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../Auth/AuthContext';
import { getUserStats, type UserStatsResponse } from './DashboardService';
import { getRecommendation } from '../QuestionnairePage/QuestionnaireService';
import './DashboardPage.css';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const [recommendation, setRecommendation] = useState<Record<string, string> | null>(null);
  const [recLoading, setRecLoading] = useState(true);

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

    const fetchRec = async () => {
      try {
        const data = await getRecommendation();
        if (data) {
          setRecommendation(data);
        }
      } catch (error) {
        console.error("Failed to fetch recommendation", error);
      } finally {
        setRecLoading(false);
      }
    };

    fetchStats();
    fetchRec();
  }, []);

  const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const todayName = daysOfWeek[new Date().getDay()];
  const todaysWorkout = recommendation ? recommendation[todayName] : null;

  const parseWorkout = (raw: string) => {
    const match = raw.match(/^(.+?)\s*\((.+)\)$/);
    if (match) {
      return {
        title: match[1].trim(),
        details: match[2].split(',').map(item => item.trim())
      };
    }
    return { title: raw, details: [] };
  };

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

              <div className="dashboard-section rec-section">
                <h2 className="section-title">Today's Focus</h2>
                {recLoading ? (
                  <div className="loading-rec">Loading your daily focus...</div>
                ) : recommendation ? (
                  <div className="recommendation-card active-state">
                    <div className="card-badge">{todayName}'s Recommendation</div>
                    {todaysWorkout ? (
                      (() => {
                        const { title, details } = parseWorkout(todaysWorkout);
                        return (
                          <div className="workout-info">
                            <h3 className="workout-title">{title}</h3>
                            {details.length > 0 ? (
                              <ul className="workout-exercises">
                                {details.map((exercise, idx) => (
                                  <li key={idx} className="exercise-item">
                                    <span className="bullet">⚡</span>
                                    {exercise}
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              <p className="rest-hint">Perfect day for active recovery or complete rest.</p>
                            )}
                          </div>
                        );
                      })()
                    ) : (
                      <p className="no-workout">Rest Day! Keep up the recovery.</p>
                    )}
                  </div>
                ) : (
                  <div className="recommendation-card empty-state">
                    <h3>Start Your Tailored Routine</h3>
                    <p>Take our quick fitness assessment to generate a custom 7-day schedule and get daily guidance.</p>
                    <Link to="/questionnaire" className="cta-btn">Take Assessment</Link>
                  </div>
                )}
              </div>

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

