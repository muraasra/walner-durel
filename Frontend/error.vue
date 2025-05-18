<script setup lang="ts">
import type { NuxtError } from "#app";

const props = defineProps({
  error: Object as () => NuxtError,
});

const handleError = () => clearError({ redirect: "/" });
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-gray-800 dark:text-gray-200 mb-4">
        {{ error?.statusCode }}
      </h1>
      <p class="text-xl text-gray-600 dark:text-gray-400 mb-8">
        {{ error?.message }}
      </p>
      <button
        @click="handleError"
        class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors"
      >
        Retour à l'accueil
      </button>
    </div>
  </div>
</template>
