import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_BASE_URL = '/api/';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    }
});

api.interceptors.request.use(
    (config) => {
        const token = useAuthStore.getState().accessToken;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Don't try to refresh for login requests or multiple times
        if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url.includes('auth/login')) {
            originalRequest._retry = true;
            try {
                const refreshToken = useAuthStore.getState().refreshToken;
                if (!refreshToken) throw new Error('No refresh token available');

                const res = await axios.post(`${API_BASE_URL}auth/token/refresh/`, {
                    refresh: refreshToken
                });

                const { access } = res.data;
                useAuthStore.getState().updateAccessToken(access);
                originalRequest.headers.Authorization = `Bearer ${access}`;
                return api(originalRequest);
            } catch (err) {
                useAuthStore.getState().logout();
                return Promise.reject(err);
            }
        }
        return Promise.reject(error);
    }
);

export default api;
