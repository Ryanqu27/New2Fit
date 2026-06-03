import api from '../../api';

export interface UserSettings {
    id: number;
    user_id: number;
    theme: 'light' | 'dark';
    unit_preference: 'imperial' | 'metric';
    camera_framerate_preference: 30 | 60;
    language: string;
    workout_reminders: boolean;
}

export interface SettingsUpdate {
    theme?: 'light' | 'dark';
    unit_preference?: 'imperial' | 'metric';
    camera_framerate_preference?: 30 | 60;
    language?: string;
    workout_reminders?: boolean;
}

export const SettingsService = {
    getSettings: async (): Promise<UserSettings> => {
        const response = await api.get<UserSettings>('/settings/');
        return response.data;
    },

    updateSettings: async (settingsUpdate: SettingsUpdate): Promise<UserSettings> => {
        const response = await api.put<UserSettings>('/settings/', settingsUpdate);
        return response.data;
    }
};
