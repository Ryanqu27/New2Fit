import axios from 'axios';

// Abstraction on axios to make API calls easier and more consistent
const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json'},
});

// Automatically attach the Google token to every request if the user is logged in
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('google_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;