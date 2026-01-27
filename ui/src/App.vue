<script setup lang="ts">
import { useAuthStore } from './presentation/state/authStore';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const logout = () => {
    authStore.logout();
    router.push('/login');
};
</script>

<template>
  <div class="app-layout">
    <nav v-if="authStore.isAuthenticated" class="navbar">
        <div class="nav-brand">Vision System</div>
        <div class="nav-links">
            <router-link to="/">En Vivo</router-link>
            <router-link to="/events">Eventos</router-link>
            <button @click="logout" class="btn-logout">Salir</button>
        </div>
    </nav>
    <main class="main-content">
        <router-view></router-view>
    </main>
  </div>
</template>

<style>
/* Global resets */
body {
    margin: 0;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background-color: #0f172a;
    color: #e2e8f0;
}

.app-layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
}

.nav-brand {
    font-weight: 700;
    font-size: 1.25rem;
    color: #38bdf8;
}

.nav-links {
    display: flex;
    gap: 1.5rem;
    align-items: center;
}

.nav-links a {
    text-decoration: none;
    color: #94a3b8;
    transition: color 0.2s;
}

.nav-links a:hover, .nav-links a.router-link-active {
    color: white;
}

.btn-logout {
    background: transparent;
    border: 1px solid #ef4444;
    color: #ef4444;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-logout:hover {
    background: #ef4444;
    color: white;
}

.main-content {
    flex: 1;
    position: relative;
}
</style>
