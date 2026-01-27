<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../state/authStore';

const username = ref('');
const password = ref('');
const errorMsg = ref('');
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  errorMsg.value = '';
  const success = await authStore.login(username.value, password.value);
  if (success) {
    router.push('/');
  } else {
    errorMsg.value = 'Usuario o contraseña incorrectos';
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">Bienvenido</h1>
      <p class="subtitle">Sistema de Visión Artificial</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label for="username">Usuario</label>
          <input 
            id="username" 
            v-model="username" 
            type="text" 
            placeholder="Introduce tu usuario" 
            required
          />
        </div>
        
        <div class="input-group">
          <label for="password">Contraseña</label>
          <input 
            id="password" 
            v-model="password" 
            type="password" 
            placeholder="Introduce tu contraseña" 
            required
          />
        </div>

        <button type="submit" class="btn-primary">
          Ingresar
        </button>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: white;
}

.login-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.title {
  font-family: 'Inter', sans-serif;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
  background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #94a3b8;
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: #cbd5e1;
}

.input-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0f172a;
  color: white;
  font-size: 1rem;
  transition: all 0.2s;
}

.input-group input:focus {
  outline: none;
  border-color: #4facfe;
  box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.2);
}

.btn-primary {
  padding: 0.85rem;
  border: none;
  border-radius: 8px;
  background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
  color: #0f172a;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-primary:active {
  transform: translateY(1px);
}

.error-msg {
  color: #ef4444;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
</style>
