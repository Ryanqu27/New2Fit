import { useEffect, useState } from 'react'
import { getQuestions, submitQuestions } from './QuestionnaireService'
import WorkoutPlan from './WorkoutPlan'
import './Questionnaire.css'

interface Question {
  question: string;
  answers: string[];
}

export default function Questionnaire() {
  const [workoutRecommendation, setWorkoutRecommendation] = useState<Record<string, string> | null>(null);
  const [questionnaire, setQuestionnaire] = useState<Question[]>([]);
  const [userAnswers, setUserAnswers] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    async function fetchQuestions() {
      const response = await getQuestions();
      setQuestionnaire(response);
      setUserAnswers(new Array(response.length).fill(""));
    }
    fetchQuestions();
  }, [])

  const handleRadioButtonChange = (questionIndex: number, answer: string) => {
    const updatedAnswers = [...userAnswers];
    updatedAnswers[questionIndex] = answer;
    setUserAnswers(updatedAnswers);
  }

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const response = await submitQuestions(userAnswers);
      setWorkoutRecommendation(response);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetake = () => {
    setWorkoutRecommendation(null);
    setUserAnswers(new Array(questionnaire.length).fill(""));
  };

  const isFormComplete = userAnswers.length > 0 && userAnswers.every(ans => ans !== "");

  if (workoutRecommendation) {
    return <WorkoutPlan plan={workoutRecommendation} onRetake={handleRetake} />;
  }

  return (
    <div className="questionnaire-container">
      <header className="q-header">
        <h2 className="q-title">Fitness Assessment</h2>
        <p className="q-sub">Let's tailor a plan specifically to your goals and experience.</p>
      </header>

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
                  )
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
  )
}