import api from '../../api';

export interface UserStatsResponse {
    all_time_workouts: number;
    all_time_minutes: number;
    this_week_workouts: number;
    this_week_minutes: number;
}

export const getUserStats = async (): Promise<UserStatsResponse> => {
    const response = await api.get('/users/me/stats');
    return response.data;
};
