import React, { createContext, useContext, useEffect, useState } from 'react';
import { SettingsService, type UserSettings } from '../pages/SettingsPage/SettingsService';

type SettingsContextType = {
    settings: UserSettings | null;
    updateSettings: (update: Partial<UserSettings>) => Promise<void>;
    loading: boolean;
};

const SettingsContext = createContext<SettingsContextType | null>(null);

export function SettingsProvider({ children }: { children: React.ReactNode }) {
    const [settings, setSettings] = useState<UserSettings | null>(null);
    const [loading, setLoading] = useState(true);

    const applyTheme = (theme: 'light' | 'dark') => {
        document.documentElement.setAttribute('data-theme', theme);
    };

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const data = await SettingsService.getSettings();
                setSettings(data);
                applyTheme(data.theme);
            } catch (error) {
                console.warn('Could not load settings:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchSettings();
    }, []);

    const updateSettings = async (update: Partial<UserSettings>) => {
        try {
            const newSettings = await SettingsService.updateSettings(update);
            setSettings(newSettings);
            if (update.theme) {
                applyTheme(update.theme);
            }
        } catch (error) {
            console.error('Failed to update settings:', error);
            throw error;
        }
    };

    return (
        <SettingsContext.Provider value={{ settings, updateSettings, loading }}>
            {children}
        </SettingsContext.Provider>
    );
}

export function useSettings() {
    const context = useContext(SettingsContext);
    if (!context) {
        throw new Error('useSettings must be used inside SettingsProvider');
    }
    return context;
}
