import React, { useState } from 'react';
import { useSettings } from '../../Settings/SettingsContext';
import './SettingsPage.css';

export default function SettingsPage() {
    const { settings, updateSettings, loading } = useSettings();
    const [saveStatus, setSaveStatus] = useState<'saving' | 'success' | 'error' | null>(null);

    const updateSetting = async (update: Parameters<typeof updateSettings>[0]) => {
        setSaveStatus('saving');
        try {
            await updateSettings(update);
            setSaveStatus('success');
            setTimeout(() => setSaveStatus(null), 3000);
        } catch {
            setSaveStatus('error');
            setTimeout(() => setSaveStatus(null), 4000);
        }
    };

    if (loading) {
        return <div className="settings-page"><p>Loading preferences...</p></div>;
    }

    if (!settings) {
        return <div className="settings-page"><p>Failed to load settings. Please try again later.</p></div>;
    }

    return (
        <div className="settings-page">
            <div className="settings-header">
                <h1>Preferences</h1>
                <p>Customize your New2Fit experience</p>
            </div>

            <div className="settings-section">
                <h2>Application</h2>
                
                <div className="setting-item">
                    <div className="setting-info">
                        <h3>Theme</h3>
                        <p>Choose your preferred interface style</p>
                    </div>
                    <div className="segmented-control">
                        <button 
                            className={settings.theme === 'light' ? 'active' : ''} 
                            onClick={() => updateSetting({ theme: 'light' })}
                        >
                            Light
                        </button>
                        <button 
                            className={settings.theme === 'dark' ? 'active' : ''} 
                            onClick={() => updateSetting({ theme: 'dark' })}
                        >
                            Dark
                        </button>
                    </div>
                </div>
            </div>

            <div className="settings-section">
                <h2>Fitness & Tracking</h2>

                <div className="setting-item">
                    <div className="setting-info">
                        <h3>Unit Preference</h3>
                        <p>Measurement system for weight and distance</p>
                    </div>
                    <div className="segmented-control">
                        <button 
                            className={settings.unit_preference === 'imperial' ? 'active' : ''} 
                            onClick={() => updateSetting({ unit_preference: 'imperial' })}
                        >
                            Imperial (lbs, mi)
                        </button>
                        <button 
                            className={settings.unit_preference === 'metric' ? 'active' : ''} 
                            onClick={() => updateSetting({ unit_preference: 'metric' })}
                        >
                            Metric (kg, km)
                        </button>
                    </div>
                </div>

                <div className="setting-item">
                    <div className="setting-info">
                        <h3>Workout Reminders</h3>
                        <p>Receive notifications for scheduled workouts</p>
                    </div>
                    <label className="toggle-switch">
                        <input 
                            type="checkbox" 
                            checked={settings.workout_reminders}
                            onChange={(e) => updateSetting({ workout_reminders: e.target.checked })}
                        />
                        <span className="slider"></span>
                    </label>
                </div>
            </div>

            <div className="settings-section">
                <h2>AI Camera</h2>

                <div className="setting-item">
                    <div className="setting-info">
                        <h3>Framerate Preference</h3>
                        <p>Prioritize AI tracking performance or save battery</p>
                    </div>
                    <div className="segmented-control">
                        <button 
                            className={settings.camera_framerate_preference === 30 ? 'active' : ''} 
                            onClick={() => updateSetting({ camera_framerate_preference: 30 })}
                        >
                            30 FPS
                        </button>
                        <button 
                            className={settings.camera_framerate_preference === 60 ? 'active' : ''} 
                            onClick={() => updateSetting({ camera_framerate_preference: 60 })}
                        >
                            60 FPS
                        </button>
                    </div>
                </div>
            </div>

            <div className="settings-section">
                <h2>Privacy & Discoverability</h2>

                <div className="setting-item">
                    <div className="setting-info">
                        <h3>Private Account</h3>
                        <p>Hide your profile from the direct messaging search results</p>
                    </div>
                    <label className="toggle-switch">
                        <input 
                            type="checkbox" 
                            checked={settings.is_private}
                            onChange={(e) => updateSetting({ is_private: e.target.checked })}
                        />
                        <span className="slider"></span>
                    </label>
                </div>
            </div>

            {saveStatus && (
                <div className={`save-status ${saveStatus}`}>
                    {saveStatus === 'saving' && "Saving changes..."}
                    {saveStatus === 'success' && "✓ Preferences saved!"}
                    {saveStatus === 'error' && "✗ Error saving preferences."}
                </div>
            )}
        </div>
    );
}
