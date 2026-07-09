import React, { useState, useEffect } from 'react';
import { useAuth } from '../../Auth/AuthContext';
import { ProfileService } from './ProfileService';
import './ProfilePage.css';

export default function ProfilePage() {
    const { user, updateUser } = useAuth();
    const [username, setUsername] = useState(user?.username || '');
    const [status, setStatus] = useState<{ type: 'error' | 'success', message: string } | null>(null);
    const [isSaving, setIsSaving] = useState(false);
    const [isUploading, setIsUploading] = useState(false);

    useEffect(() => {
        if (user?.username) {
            setUsername(user.username);
        }
    }, [user]);

    const handleUsernameSave = async () => {
        setIsSaving(true);
        setStatus(null);
        try {
            const updatedUser = await ProfileService.updateUsername(username);
            updateUser({ username: updatedUser.username });
            setStatus({ type: 'success', message: 'Username saved successfully!' });
        } catch (error: any) {
            if (error.response?.status === 409) {
                setStatus({ type: 'error', message: `@${username} is already taken.` });
            } else {
                setStatus({ type: 'error', message: 'Failed to update username.' });
            }
        } finally {
            setIsSaving(false);
        }
    };

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setIsUploading(true);
        setStatus(null);
        try {
            const updatedUser = await ProfileService.uploadProfilePicture(file);
            updateUser({ profile_picture_url: updatedUser.profile_picture_url });
            setStatus({ type: 'success', message: 'Profile picture updated!' });
        } catch (error) {
            setStatus({ type: 'error', message: 'Failed to upload profile picture.' });
        } finally {
            setIsUploading(false);
        }
    };

    if (!user) return null;

    const avatarUrl = user.profile_picture_url 
        ? `http://localhost:8000${user.profile_picture_url}` 
        : null;
        
    const initials = user.first_name ? user.first_name.charAt(0).toUpperCase() : '?';

    const joinDate = new Date(user.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    return (
        <div className="profile-page">
            <div className="profile-header">
                <h1>Your Profile</h1>
                <p>Manage your account settings and public persona</p>
            </div>

            <div className="profile-section">
                <h2>Profile Picture</h2>
                <div className="avatar-container">
                    <div className="avatar-wrapper">
                        {avatarUrl ? (
                            <img src={avatarUrl} alt="Profile" className="avatar-image" />
                        ) : (
                            <div className="avatar-initials">{initials}</div>
                        )}
                    </div>
                    <label className="avatar-upload-btn">
                        {isUploading ? 'Uploading...' : 'Change Picture'}
                        <input 
                            type="file" 
                            accept="image/png, image/jpeg, image/webp" 
                            onChange={handleFileChange} 
                            disabled={isUploading}
                        />
                    </label>
                </div>
            </div>

            <div className="profile-section">
                <h2>Username</h2>
                <div className="username-form">
                    <div className="username-input-group">
                        <label htmlFor="username">DM Display Name</label>
                        <input 
                            type="text" 
                            id="username"
                            className="username-input" 
                            placeholder="Enter a unique username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                        <small style={{ color: 'var(--text-secondary)' }}>
                            Your username will be shown instead of your real name in direct messages.
                        </small>
                    </div>
                    <button 
                        className="save-btn" 
                        onClick={handleUsernameSave}
                        disabled={isSaving || username === user?.username}
                    >
                        {isSaving ? 'Saving...' : 'Save Username'}
                    </button>
                    {status && (
                        <div className={status.type === 'error' ? 'error-message' : 'success-message'}>
                            {status.message}
                        </div>
                    )}
                </div>
            </div>

            <div className="profile-section">
                <h2>Account Information</h2>
                <div className="account-info">
                    <div className="info-item">
                        <span className="info-label">Email Address</span>
                        <span className="info-value">{user.email}</span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">First Name</span>
                        <span className="info-value">{user.first_name || 'Not provided'}</span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">Member Since</span>
                        <span className="info-value">{joinDate}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
