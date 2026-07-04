import { useEffect, useState } from 'react';
import axios from 'axios';
import { logWorkout, getWorkouts, updateWorkout, type Workout, type WorkoutRequest, type ExerciseSet } from './WorkoutsService';
import { useSettings } from '../../Settings/SettingsContext';
import { weightUnit, toDisplay, toStored } from '../../utils/units';
import './Workouts.css';

interface ExerciseFormRow {
    name: string;
    sets: number | '';
    reps: number | '';
    weight_display: string; 
}

export default function Workouts() {
    const { settings } = useSettings();
    const [workouts, setWorkouts] = useState<Workout[]>([]);
    const [totalCount, setTotalCount] = useState<number>(0);
    const [skip, setSkip] = useState<number>(0);
    const LIMIT = 10;
    
    const [name, setName] = useState('');
    const [durationMinutes, setDurationMinutes] = useState<number | ''>('');
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
    const [exerciseRows, setExerciseRows] = useState<ExerciseFormRow[]>([
        { name: '', sets: '', reps: '', weight_display: '' }
    ]);

    const [editingWorkoutId, setEditingWorkoutId] = useState<number | null>(null);

    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    const pref = settings?.unit_preference;

    useEffect(() => {
        fetchWorkouts(0);
    }, []);

    const fetchWorkouts = async (currentSkip: number, append: boolean = false) => {
        try {
            if (!append) setLoading(true);
            const data = await getWorkouts(currentSkip, LIMIT);
            if (append) {
                setWorkouts(prev => [...prev, ...data.workouts]);
            } else {
                setWorkouts(data.workouts);
            }
            setTotalCount(data.total_count);
            setSkip(currentSkip);
        } catch {
            setError('Failed to load workouts.');
        } finally {
            if (!append) setLoading(false);
        }
    };

    const handleLoadMore = () => {
        fetchWorkouts(skip + LIMIT, true);
    };

    const handleAddExercise = () => {
        setExerciseRows(prev => [...prev, { name: '', sets: '', reps: '', weight_display: '' }]);
    };

    const handleRemoveExercise = (index: number) => {
        setExerciseRows(prev => prev.filter((_, i) => i !== index));
    };

    const handleExerciseChange = (index: number, field: keyof ExerciseFormRow, value: string) => {
        setExerciseRows(prev => {
            const newRows = [...prev];
            if (field === 'name' || field === 'weight_display') {
                newRows[index] = { ...newRows[index], [field]: value };
            } else {
                newRows[index] = { ...newRows[index], [field]: value === '' ? '' : Number(value) };
            }
            return newRows;
        });
    };

    const handleEditClick = (workout: Workout) => {
        setEditingWorkoutId(workout.id);
        setName(workout.name);
        setDurationMinutes(workout.duration_minutes);
        const d = new Date(workout.date);
        setDate(d.toISOString().split('T')[0]);
        
        if (workout.exercises && workout.exercises.length > 0) {
            setExerciseRows(workout.exercises.map(ex => ({
                name: ex.name,
                sets: ex.sets || '',
                reps: ex.reps || '',
                weight_display: ex.weight_kg ? toDisplay(ex.weight_kg, pref).toString() : ''
            })));
        } else {
            setExerciseRows([{ name: '', sets: '', reps: '', weight_display: '' }]);
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleCancelEdit = () => {
        setEditingWorkoutId(null);
        setName('');
        setDurationMinutes('');
        setDate(new Date().toISOString().split('T')[0]);
        setExerciseRows([{ name: '', sets: '', reps: '', weight_display: '' }]);
        setError(null);
        setSuccess(false);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        setError(null);
        setSuccess(false);

        try {
            const exercisesPayload: ExerciseSet[] = exerciseRows
                .filter(row => row.name.trim() !== '') // Skip completely empty rows
                .map(row => ({
                    name: row.name,
                    sets: row.sets === '' ? 0 : Number(row.sets),
                    reps: row.reps === '' ? 0 : Number(row.reps),
                    weight_kg: toStored(row.weight_display, pref) || 0 // Store bodyweight/empty as 0 or null
                }));

            const payload: WorkoutRequest = {
                name,
                duration_minutes: Number(durationMinutes),
                date: new Date(date).toISOString(),
                exercises: exercisesPayload
            };

            if (editingWorkoutId) {
                await updateWorkout(editingWorkoutId, payload);
                setSuccess(true);
                handleCancelEdit();
            } else {
                await logWorkout(payload);
                setSuccess(true);
                
                // Reset form
                setName('');
                setDurationMinutes('');
                setDate(new Date().toISOString().split('T')[0]);
                setExerciseRows([{ name: '', sets: '', reps: '', weight_display: '' }]);
            }
            
            await fetchWorkouts(0);
        } catch (err) {
            if (axios.isAxiosError(err)) {
                const message = err.response?.data?.detail || 'Failed to save workout. Please try again.';
                setError(message);
            } else {
                setError('Failed to save workout. Please try again.');
            }
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
                    <h2 className="section-title">{editingWorkoutId ? 'Update Workout' : 'Log a Workout'}</h2>
                    <form className="log-form" onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="workout-name">Workout Name</label>
                            <input
                                id="workout-name"
                                type="text"
                                placeholder="e.g. Push Day, Leg Day"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="workout-duration">Duration (minutes)</label>
                                <input
                                    id="workout-duration"
                                    type="number"
                                    min="1"
                                    placeholder="45"
                                    value={durationMinutes}
                                    onChange={(e) => setDurationMinutes(e.target.value === '' ? '' : Number(e.target.value))}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="workout-date">Date</label>
                                <input
                                    id="workout-date"
                                    type="date"
                                    value={date}
                                    onChange={(e) => setDate(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        {/* Exercise Builder */}
                        <div className="exercise-builder">
                            <label className="exercise-builder-label">Exercises</label>
                            
                            <div className="exercise-rows">
                                {exerciseRows.map((row, idx) => (
                                    <div key={idx} className="exercise-row">
                                        <input 
                                            className="ex-name" 
                                            placeholder="Exercise (e.g. Bench Press)" 
                                            value={row.name}
                                            onChange={(e) => handleExerciseChange(idx, 'name', e.target.value)}
                                            required
                                        />
                                        <input 
                                            className="ex-sets" 
                                            type="number" 
                                            min="0"
                                            placeholder="Sets" 
                                            value={row.sets}
                                            onChange={(e) => handleExerciseChange(idx, 'sets', e.target.value)}
                                        />
                                        <input 
                                            className="ex-reps" 
                                            type="number" 
                                            min="0"
                                            placeholder="Reps" 
                                            value={row.reps}
                                            onChange={(e) => handleExerciseChange(idx, 'reps', e.target.value)}
                                        />
                                        <div className="ex-weight-wrapper">
                                            <input 
                                                className="ex-weight" 
                                                type="number"
                                                min="0"
                                                step="0.1" 
                                                placeholder="Weight" 
                                                value={row.weight_display}
                                                onChange={(e) => handleExerciseChange(idx, 'weight_display', e.target.value)}
                                            />
                                            <span className="unit-badge">{weightUnit(pref)}</span>
                                        </div>
                                        <button 
                                            type="button" 
                                            className="ex-remove"
                                            onClick={() => handleRemoveExercise(idx)}
                                            disabled={exerciseRows.length === 1}
                                            title="Remove Exercise"
                                        >
                                            ✕
                                        </button>
                                    </div>
                                ))}
                            </div>
                            
                            <button type="button" className="add-exercise-btn" onClick={handleAddExercise}>
                                + Add Exercise
                            </button>
                        </div>

                        {error && <p className="form-error">{error}</p>}
                        {success && <p className="form-success">Workout {editingWorkoutId ? 'updated' : 'logged'}!</p>}

                        <div className="form-actions">
                            <button
                                id="log-workout-btn"
                                type="submit"
                                className="log-btn"
                                disabled={submitting || exerciseRows.length === 0}
                            >
                                {submitting ? (editingWorkoutId ? 'Updating...' : 'Logging...') : (editingWorkoutId ? 'Update Workout' : 'Log Workout')}
                            </button>
                            {editingWorkoutId && (
                                <button
                                    type="button"
                                    className="cancel-btn"
                                    onClick={handleCancelEdit}
                                    disabled={submitting}
                                >
                                    Cancel
                                </button>
                            )}
                        </div>
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
                                        <button 
                                            className="edit-workout-btn" 
                                            onClick={() => handleEditClick(workout)}
                                            title="Edit Workout"
                                        >
                                            ✎ Edit
                                        </button>
                                    </div>
                                    
                                    {workout.exercises && workout.exercises.length > 0 && (
                                        <div className="workout-exercises-list">
                                            <div className="ex-list-header">
                                                <span>Exercise</span>
                                                <span>Sets</span>
                                                <span>Reps</span>
                                                <span>Weight</span>
                                            </div>
                                            {workout.exercises.map((ex, idx) => (
                                                <div key={idx} className="ex-list-row">
                                                    <span>{ex.name}</span>
                                                    <span>{ex.sets || '-'}</span>
                                                    <span>{ex.reps || '-'}</span>
                                                    <span>
                                                        {ex.weight_kg ? `${toDisplay(ex.weight_kg, pref)} ${weightUnit(pref)}` : 'Bodyweight'}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </li>
                            ))}
                        </ul>
                    )}
                    
                    {!loading && workouts.length > 0 && workouts.length < totalCount && (
                        <button className="log-btn load-more-btn" type="button" onClick={handleLoadMore} style={{ marginTop: '20px' }}>
                            Load More
                        </button>
                    )}
                </section>
            </div>
        </div>
    );
}