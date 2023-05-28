import axios from "axios";
import { makeAutoObservable } from "mobx";
import { API_URL } from "../http";
import { IUser } from "../models/IUser";
import { AuthResponse } from "../models/response/AuthResponse";
import AuthServices from "../services/AuthServices";

export default class UserStore {
    user = {} as IUser;
    isAuth = false;
    isLoading = false;

    constructor() {
        makeAutoObservable(this);
    }

    setAuth(bool: boolean) {
        this.isAuth = bool;
    }

    setUser(user: IUser) {
        this.user = user;
    }

    setLoading(bool: boolean) {
        this.isLoading = bool;
    }

    async login(email: string, password: string, role: string) {
        try {
            const response = await AuthServices.login(email, password, role);
            localStorage.setItem('token', response.data.accessToken);
            localStorage.setItem('rtoken', response.data.refreshToken);
            this.setAuth(true);
            this.setUser(response.data.user);
        } catch (e: any) {
            console.log(e.response?.data?.message);
        }
    }

    async registration(username: string, email: string, password: string) {
        try {
            const response = await AuthServices.registration(username, email, password);
            localStorage.setItem('token', response.data.accessToken);
            localStorage.setItem('rtoken', response.data.refreshToken);
            this.setAuth(true);
            this.setUser(response.data.user);
        } catch (e: any) {
            console.log(e.response?.data?.message);
        }
    }

    async logout() {
        try {
            const response = await AuthServices.logout();
            console.table(response);
            localStorage.removeItem('token');
            localStorage.removeItem('rtoken');
            this.setAuth(false);
            this.setUser({} as IUser);
        } catch (e: any) {
            console.log(e.response?.data?.message);
        } 
    }

    async checkAuth() {
        this.setLoading(true);
        try {
            const response = await axios.post<AuthResponse>(`${API_URL}/users/refresh`, {refreshToken: `${localStorage.getItem('rtoken')}`, } );
            localStorage.setItem('token', response.data.accessToken);
            localStorage.setItem('rtoken', response.data.refreshToken);
            this.setAuth(true);
            this.setUser(response.data.user);
        } catch (e: any) {
            console.log(e.response?.data?.message);
        } finally {
            this.setLoading(false);
        }
    }
}
