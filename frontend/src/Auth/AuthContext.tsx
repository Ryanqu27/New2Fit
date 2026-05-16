import React, { createContext, useContext, useState } from 'react';

type User = {
    email: string;
    first_name: string;
    created_at: string;
}

type AuthContextType = {
    user: User | null;
    login: (user: User, token: string) => void;
    logout: () => void;
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

    const login = (inputUser: User, token: string) => {
        setUser(inputUser);
        localStorage.setItem('user', JSON.stringify(inputUser));
        localStorage.setItem('google_token', token);
    }

    const logout = () => {
        setUser(null);
        localStorage.removeItem('user');
        localStorage.removeItem('google_token');
    }

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
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