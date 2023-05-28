import axios from "axios";
import { AuthResponse } from "../models/response/AuthResponse";

export const API_URL = `http://178.170.192.87:8000`;

const $api = axios.create({
    withCredentials: true,
    baseURL: API_URL,
}); 

$api.interceptors.request.use((config) => {
    config.headers.Authorization = `Bearer ${localStorage.getItem('token')}`;
    return config;
});

$api.interceptors.response.use((config) => {
    return config;
},async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && error.config && !error.config._isRetry) {
        originalRequest._isRetry = true;
        try {
            const response = await axios.post<AuthResponse>(`${API_URL}/users/refresh`, {refreshToken: `${localStorage.getItem('rtoken')}`});
            localStorage.setItem('token', response.data.accessToken);
            localStorage.setItem('rtoken', response.data.accessToken);
            return $api.request(originalRequest);
        } catch (e) {
            console.log('Пользователь не авторизован', e);
        }
        throw error;
    };
});

export default $api;