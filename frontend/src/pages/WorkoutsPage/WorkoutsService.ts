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

export interface WorkoutResponse {
    workouts: Workout[];
    total_count: number;
}

export const getWorkouts = async (skip: number = 0, limit: number = 10): Promise<WorkoutResponse> => {
    const response = await api.get('/workouts', { params: { skip, limit } });
    return response.data;
};

export const updateWorkout = async (id: number, workout: WorkoutRequest): Promise<void> => {
    await api.put(`/workouts/${id}`, workout);
};