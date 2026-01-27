import axios from 'axios';

// Assuming API runs on port 8000
const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded', // OAuth2 standard
    },
});

export default apiClient;
