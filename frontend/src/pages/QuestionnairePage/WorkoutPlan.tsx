import './WorkoutPlan.css'

interface WorkoutPlanProps {
  plan: Record<string, string>;
  onRetake: () => void;
}

const dayMeta: Record<string, { accent: string }> = {
  Monday:    { accent: 'var(--day-mon)' },
  Tuesday:   { accent: 'var(--day-tue)' },
  Wednesday: { accent: 'var(--day-wed)' },
  Thursday:  { accent: 'var(--day-thu)' },
  Friday:    { accent: 'var(--day-fri)' },
  Saturday:  { accent: 'var(--day-sat)' },
  Sunday:    { accent: 'var(--day-sun)' },
};

function parseWorkout(raw: string): { title: string; details: string } {
  const match = raw.match(/^(.+?)\s*\((.+)\)$/);
  if (match) {
    return { title: match[1].trim(), details: match[2].trim() };
  }
  return { title: raw, details: '' };
}

export default function WorkoutPlan({ plan, onRetake }: WorkoutPlanProps) {
  const days = Object.entries(plan);

  return (
    <div className="workout-plan-root">
      <header className="wp-hero">
        <h1 className="wp-title">Your Workout Plan</h1>
        <p className="wp-sub">
          Here is your personalized workout recommendation!
          <br />Feel free to change up exercises as necessary
        </p>
      </header>

      <div className="wp-grid">
        {days.map(([day, workout], i) => {
          const meta = dayMeta[day] ?? { accent: 'var(--accent)' };
          const { title, details } = parseWorkout(workout);

          return (
            <article
              key={day}
              className="wp-card"
              style={
                { '--card-accent': meta.accent, '--card-index': i } as React.CSSProperties
              }
            >
              <div className="wp-card-header">
                <span className="wp-card-day">{day}</span>
              </div>

              <h3 className="wp-card-title">{title}</h3>

              {details && (
                <ul className="wp-card-details">
                  {details.split(',').map((item, idx) => (
                    <li key={idx}>{item.trim()}</li>
                  ))}
                </ul>
              )}
            </article>
          );
        })}
      </div>

      <button className="wp-retake" onClick={onRetake}>
        ↻ Retake Questionnaire
      </button>
    </div>
  );
}
