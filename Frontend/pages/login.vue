<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import { useAuthStore } from '@/stores/auth';

import { useRouter } from 'vue-router'

definePageMeta({
  layout: 'auth',
})
const auth = useAuthStore()
const router = useRouter()
type LoginResponse = {
  access: string
  refresh: string
  user_id: number
  username: string
};
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  if (!username.value || !password.value) {
    error.value = 'Veuillez remplir tous les champs'
    loading.value = false
    return
  }
  try {
    const { data, error: fetchError } = await useFetch<LoginResponse>('http://127.0.0.1:8000/api/token/', {
      method: 'POST',
      body: {
        username: username.value,
        password: password.value
      },
      server: false
    });
    
    if (fetchError.value || !data.value?.access) {
      error.value = 'Identifiants incorrects';
      loading.value = false;
      return;
    }

    auth.setToken(data.value.access);
    auth.setUser({
      id: data.value.user_id ?? 0,
      username: username.value
    });

    await nextTick();
    router.push('/');
  } catch (err) {
    
    console.error(err);
    error.value = 'Erreur lors de la connexion';
  } finally {
    loading.value = false;
  }
  
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-lg">
      <h1 class="text-2xl font-semibold mb-6 text-center">Connexion</h1>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-sm font-medium">Nom d'utilisateur</label>
          <input
            v-model="username"
            type="text"
            class="w-full mt-1 p-3 border rounded"
            placeholder="ex: admin"
          />
        </div>

        <div>
          <label class="block text-sm font-medium">Mot de passe</label>
          <input
            v-model="password"
            type="password"
            class="w-full mt-1 p-3 border rounded"
            placeholder="••••••••"
          />
        </div>

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-emerald-600 text-white py-3 rounded hover:bg-emerald-700"
        >
          {{ loading ? 'Connexion...' : 'Se connecter' }}
        </button>
      </form>
    </div>
  </div>
</template>
