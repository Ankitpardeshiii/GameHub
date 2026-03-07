import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
    persist(
        (set) => ({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,

            setAuth: (user, access, refresh) => set({
                user,
                accessToken: access,
                refreshToken: refresh,
                isAuthenticated: true
            }),

            logout: () => set({
                user: null,
                accessToken: null,
                refreshToken: null,
                isAuthenticated: false
            }),

            updateAccessToken: (access) => set({ accessToken: access })
        }),
        {
            name: 'gamehub-auth'
        }
    )
);
