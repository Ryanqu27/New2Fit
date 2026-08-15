import axios from 'axios';


// Abstraction on axios to make API calls easier and more consistent
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
export const BACKEND_BASE_URL = API_BASE_URL.replace(/\/api\/?$/, '');

export const getAvatarUrl = (path?: string | null): string | null => {
    if (!path) return null;
    if (path.startsWith('http://') || path.startsWith('https://')) {
        return path;
    }
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${BACKEND_BASE_URL}${cleanPath}`;
};

export const getWsBaseUrl = (): string => {
    if (import.meta.env.VITE_WS_BASE_URL) {
        return import.meta.env.VITE_WS_BASE_URL.replace(/\/+$/, '');
    }
    const protocol = window.location.protocol === 'https:' || BACKEND_BASE_URL.startsWith('https:') ? 'wss:' : 'ws:';
    const host = BACKEND_BASE_URL.replace(/^https?:\/\//, '');
    return `${protocol}//${host}/api`;
};

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json'},
    withCredentials: true, // Automatically send HttpOnly cookies on every request
});


// Automatically log user out for 401 or 403 status codes returned.
// We dispatch a custom event instead of doing a hard redirect so that
// React Router can handle the navigation (no full page reload).
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 || error.response?.status === 403) {
            localStorage.removeItem('user');
            if (window.location.pathname !== '/login') {
                window.dispatchEvent(new Event('unauthorized'));
            }
        }
        if (error.response?.status === 429) {
            error.userMessage = 'Too many requests. Please wait a moment and try again.';
        }
        return Promise.reject(error);
    }
);


export default api;