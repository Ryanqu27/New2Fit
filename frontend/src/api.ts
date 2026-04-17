import axios from 'axios';

// Abstraction on axios to make API calls easier and more consistent
const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json'},
});

export default api;