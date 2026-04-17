import { useEffect, useState } from 'react'
import { getQuestions } from './QuestionnaireService'
import './Questionnaire.css'

interface Question {
  question: string;
  answers: string[];
}

interface WorkoutPlan {
  Monday: string;
  Tuesday: string;
  Wednesday: string;
  Thursday: string;
  Friday: string;
  Saturday: string;
  Sunday: string;
}



export default function Questionnaire() {
  const [workoutRecommendation, setWorkoutRecommendation] = useState<WorkoutPlan>(null);
  const [questionnaire, setQuestionnaire] = useState<Question[]>([]);
  const [userAnswers, setUserAnswers] = useState<string[]>([]);

  useEffect(() => {
    async function fetchQuestions() {
      const response = await getQuestions();
      setQuestionnaire(response);
    }
    fetchQuestions();
  }, [])


  return (
    <div className="questionnaire-container">
      <h2>Questionnaire</h2>
      {questionnaire.length === 0 ? (
        <p>Loading questions...</p>
      ) : (
        questionnaire.map((q, index) => (
          <div key={index} className="question-card">
            <h3>{q.question}</h3>
            <ul>
              {q.answers.map((answer, ansIndex) => (
                <li key={ansIndex}>{answer}</li>
              ))}
            </ul>
          </div>
        ))
      )}
    </div>
  )
}