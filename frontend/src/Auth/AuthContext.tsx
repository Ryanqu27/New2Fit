import React, { createContext, useContext, useState } from 'react';
import api from '../api';

type User = {
    email: string;
    first_name: string;
    username?: string;
    profile_picture_url?: string;
    created_at: string;
}

type AuthContextType = {
    user: User | null;
    login: (user: User) => void;
    logout: () => void;
    updateUser: (update: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(() => {
        try {
            const saved = localStorage.getItem('user');
            return saved ? JSON.parse(saved) : null;
        } catch {
            localStorage.removeItem('user');
            return null;
        }
    })

    const login = (inputUser: User) => {
        setUser(inputUser);
        localStorage.setItem('user', JSON.stringify(inputUser));
    }

    const logout = async () => {
        try {
            // Hit the backend to clear the HttpOnly cookie
            await api.post('/users/logout');
        } catch (error) {
            console.error("Error during backend logout", error);
        } finally {
            setUser(null);
            localStorage.removeItem('user');
            // Make sure to remove old google_token if it still exists from previous sessions
            localStorage.removeItem('google_token'); 
            window.location.href = '/login';
        }
    }

    const updateUser = (update: Partial<User>) => {
        if (user) {
            const updated = { ...user, ...update };
            setUser(updated);
            localStorage.setItem('user', JSON.stringify(updated));
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, updateUser }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used inside AuthProvider");
    }
    return context;
}