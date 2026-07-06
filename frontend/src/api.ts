import axios from 'axios';


// Abstraction on axios to make API calls easier and more consistent
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json'},
    withCredentials: true, // Automatically send HttpOnly cookies on every request
});


// Automatically log user out for 401 or 403 status codes returned
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 || error.response?.status === 403) {
            localStorage.removeItem('user');
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);


export default api;