import { defineStore } from 'pinia';
import apiClient from '../../infrastructure/http/axios_client';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
    const token = ref<string | null>(localStorage.getItem('token'));
    const user = ref<string | null>(null);

    const isAuthenticated = computed(() => !!token.value);

    async function login(username: string, password: string): Promise<boolean> {
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await apiClient.post('/token', formData);

            token.value = response.data.access_token;
            localStorage.setItem('token', token.value || '');

            // Setup default header for future requests if needed, 
            // though keeping it simple here.
            return true;
        } catch (error) {
            console.error('Login failed', error);
            return false;
        }
    }

    function logout() {
        token.value = null;
        user.value = null;
        localStorage.removeItem('token');
        // Redirect logic usually handled in component or specialized service, 
        // but store provides the state mutation.
    }

    return {
        token,
        user,
        isAuthenticated,
        login,
        logout
    };
});
