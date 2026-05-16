import { useEffect, useState } from 'react';
import { logWorkout, getWorkouts, type Workout, type WorkoutRequest } from './WorkoutsService';
import './Workouts.css';

const EMPTY_FORM: WorkoutRequest = {
    name: '',
    notes: '',
    duration_minutes: 0,
    date: new Date().toISOString().split('T')[0], // default to today
};

export default function Workouts() {
    const [workouts, setWorkouts] = useState<Workout[]>([]);
    const [form, setForm] = useState<WorkoutRequest>(EMPTY_FORM);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        fetchWorkouts();
    }, []);

    const fetchWorkouts = async () => {
        try {
            setLoading(true);
            const data = await getWorkouts();
            setWorkouts(data);
        } catch {
            setError('Failed to load workouts.');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setForm(prev => ({
            ...prev,
            [name]: name === 'duration_minutes' ? Number(value) : value,
        }));
    };

    const handleSubmit = async (e: { preventDefault: () => void; }) => {
        e.preventDefault();
        setSubmitting(true);
        setError(null);
        setSuccess(false);
        try {
            // Convert date string to ISO datetime for the backend
            const payload: WorkoutRequest = {
                ...form,
                date: new Date(form.date).toISOString(),
            };
            await logWorkout(payload);
            setSuccess(true);
            setForm(EMPTY_FORM);
            await fetchWorkouts();
        } catch (err: any) {
            const message = err.response?.data?.detail || 'Failed to log workout. Please try again.';
            setError(message);
        } finally {
            setSubmitting(false);
        }
    };

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString('en-US', {
            weekday: 'short', month: 'short', day: 'numeric', year: 'numeric',
        });
    };

    return (
        <div className="workouts-page">
            <div className="workouts-header">
                <h1 className="workouts-title">Workout Log</h1>
                <p className="workouts-subtitle">Log and track your workout progress</p>
            </div>

            <div className="workouts-content">
                <section className="log-section">
                    <h2 className="section-title">Log a Workout</h2>
                    <form className="log-form" onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="workout-name">Workout Name</label>
                            <input
                                id="workout-name"
                                name="name"
                                type="text"
                                placeholder="e.g. Push Day, Leg Day"
                                value={form.name}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="workout-duration">Duration (minutes)</label>
                                <input
                                    id="workout-duration"
                                    name="duration_minutes"
                                    type="number"
                                    min="1"
                                    placeholder="45"
                                    value={form.duration_minutes || ''}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="workout-date">Date</label>
                                <input
                                    id="workout-date"
                                    name="date"
                                    type="date"
                                    value={form.date}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="workout-notes">Notes</label>
                            <textarea
                                id="workout-notes"
                                name="notes"
                                placeholder="How did it go?"
                                value={form.notes}
                                onChange={handleChange}
                                rows={3}
                                required
                            />
                        </div>

                        {error && <p className="form-error">{error}</p>}
                        {success && <p className="form-success">Workout logged!</p>}

                        <button
                            id="log-workout-btn"
                            type="submit"
                            className="log-btn"
                            disabled={submitting}
                        >
                            {submitting ? 'Logging...' : 'Log Workout'}
                        </button>
                    </form>
                </section>

                <section className="history-section">
                    <h2 className="section-title">Past Workouts</h2>
                    {loading ? (
                        <div className="workouts-loading">Loading your workouts...</div>
                    ) : workouts.length === 0 ? (
                        <div className="workouts-empty">
                            <p>No workouts logged yet.</p>
                            <p>Log your first session above!</p>
                        </div>
                    ) : (
                        <ul className="workout-list">
                            {workouts.map(workout => (
                                <li key={workout.id} className="workout-card">
                                    <div className="workout-card-header">
                                        <span className="workout-name">{workout.name}</span>
                                        <span className="workout-date">{formatDate(workout.date)}</span>
                                    </div>
                                    <div className="workout-card-meta">
                                        <span className="workout-duration">⏱ {workout.duration_minutes} min</span>
                                    </div>
                                    {workout.notes && (
                                        <p className="workout-notes">{workout.notes}</p>
                                    )}
                                </li>
                            ))}
                        </ul>
                    )}
                </section>
            </div>
        </div>
    );
}