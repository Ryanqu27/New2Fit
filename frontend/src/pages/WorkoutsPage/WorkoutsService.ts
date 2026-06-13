import api from '../../api';

export interface ExerciseSet {
    name: string;
    sets: number;
    reps: number;
    weight_kg: number;
}

export interface WorkoutRequest {
    name: string;
    exercises: ExerciseSet[];
    duration_minutes: number;
    date: string; // ISO string "2025-05-16T00:00:00"
}

export interface Workout {
    id: number;
    user_id: number;
    name: string;
    exercises: ExerciseSet[];
    duration_minutes: number;
    date: string;
}

export const logWorkout = async (workout: WorkoutRequest): Promise<void> => {
    await api.post('/workouts/log', workout);
};

export const getWorkouts = async (): Promise<Workout[]> => {
    const response = await api.get('/workouts');
    return response.data.workouts;
};