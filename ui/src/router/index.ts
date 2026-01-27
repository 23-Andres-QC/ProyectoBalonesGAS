import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../presentation/state/authStore';

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('../presentation/pages/LiveViewPage.vue'), // Default to LiveView or a Dashboard
        meta: { requiresAuth: true }
    },
    {
        path: '/events',
        name: 'Events',
        component: () => import('../presentation/pages/EventsPage.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('../presentation/pages/LoginPage.vue')
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next({ name: 'Login' });
    } else {
        next();
    }
});

export default router;
