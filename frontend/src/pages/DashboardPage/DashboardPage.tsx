import { useEffect, useState } from 'react';
import { useAuth } from '../../Auth/AuthContext';
import { getUserStats, type UserStatsResponse } from './DashboardService';
import { getQuestions, submitQuestions, getRecommendation } from './QuestionnaireService';
import WorkoutPlan from './WorkoutPlan';
import './DashboardPage.css';

interface Question {
  question: string;
  answers: string[];
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const [recommendation, setRecommendation] = useState<Record<string, string> | null>(null);
  const [recLoading, setRecLoading] = useState(true);

  // Questionnaire state
  const [questionnaire, setQuestionnaire] = useState<Question[]>([]);
  const [userAnswers, setUserAnswers] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);

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

  // Load questionnaire questions when user wants to take/retake
  useEffect(() => {
    if (showQuestionnaire) {
      const loadQuestions = async () => {
        try {
          const questionsResponse = await getQuestions();
          setQuestionnaire(questionsResponse);
          setUserAnswers(new Array(questionsResponse.length).fill(""));
        } catch (err) {
          console.error("Failed to load questions", err);
        }
      };
      loadQuestions();
    }
  }, [showQuestionnaire]);

  const handleRadioButtonChange = (questionIndex: number, answer: string) => {
    const updatedAnswers = [...userAnswers];
    updatedAnswers[questionIndex] = answer;
    setUserAnswers(updatedAnswers);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const response = await submitQuestions(userAnswers);
      setRecommendation(response);
      setShowQuestionnaire(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetake = () => {
    setRecommendation(null);
    setShowQuestionnaire(true);
  };

  const handleStartAssessment = () => {
    setShowQuestionnaire(true);
  };

  const handleCancelAssessment = () => {
    setShowQuestionnaire(false);
    setUserAnswers([]);
  };

  const isFormComplete = userAnswers.length > 0 && userAnswers.every(ans => ans !== "");

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
          Welcome <span className="home-name">{user?.first_name || 'there'}</span>
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
                ) : !showQuestionnaire ? (
                  <div className="recommendation-card empty-state">
                    <h3>Start Your Tailored Routine</h3>
                    <p>Take our quick fitness assessment to generate a custom 7-day schedule and get daily guidance.</p>
                    <button className="cta-btn" onClick={handleStartAssessment}>Take Assessment</button>
                  </div>
                ) : null}
              </div>

              {/* Inline Questionnaire */}
              {showQuestionnaire && !recommendation && (
                <div className="dashboard-section questionnaire-inline">
                  <div className="questionnaire-inline-header">
                    <h2 className="section-title">Fitness Assessment</h2>
                    <button className="q-cancel-btn" onClick={handleCancelAssessment}>✕ Cancel</button>
                  </div>
                  <p className="q-inline-sub">Let's tailor a plan specifically to your goals and experience.</p>

                  {questionnaire.length === 0 ? (
                    <div className="q-loading">Loading questions...</div>
                  ) : (
                    <div className="q-list">
                      {questionnaire.map((q, qIndex) => (
                        <div key={qIndex} className="question-card">
                          <h3 className="q-card-title">
                            <span className="q-number">{qIndex + 1}.</span> {q.question}
                          </h3>
                          <ul className="q-answers">
                            {q.answers.map((answer, ansIndex) => {
                              const isSelected = userAnswers[qIndex] === answer;
                              return (
                                <li key={ansIndex} className={`answer-item ${isSelected ? 'selected' : ''}`}>
                                  <label className="answer-label">
                                    <input
                                      type="radio"
                                      name={`question-${qIndex}`}
                                      value={answer}
                                      checked={isSelected}
                                      onChange={() => handleRadioButtonChange(qIndex, answer)}
                                      className="answer-input"
                                    />
                                    <span className="answer-text">{answer}</span>
                                  </label>
                                </li>
                              );
                            })}
                          </ul>
                        </div>
                      ))}
                      <div className="q-footer">
                        <button
                          className="submit-button"
                          onClick={handleSubmit}
                          disabled={!isFormComplete || isSubmitting}
                        >
                          {isSubmitting ? 'Generating...' : 'Get My Workout Plan'}
                        </button>
                        {!isFormComplete && (
                          <p className="q-hint">Please answer all questions to continue.</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Full Workout Plan section */}
              {recommendation && (
                <div className="dashboard-section">
                  <WorkoutPlan plan={recommendation} onRetake={handleRetake} />
                </div>
              )}

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
