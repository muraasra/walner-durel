<script setup>
import { ref } from "vue";

// Liste des utilisateurs (exemple)
const utilisateurs = ref([
  { nom: "fok", role: "superadmin", motDePasse: "12345" },
  { nom: "durel", role: "admin", motDePasse: "raoul ???" },
  { nom: "tayou", role: "user", motDePasse: "raoul" },
]);
</script>

<template>
  <div class="mt-5 px-6">
    <!-- En-tête -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl md:text-3xl font-bold text-blue-400">Utilisateurs</h2>
    </div>

    <!-- Liste des utilisateurs -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="(user, index) in utilisateurs" :key="index" class="p-6 bg-white shadow rounded-xl flex flex-col items-center border border-blue-100 hover:shadow-lg transition">
        <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mb-3">
          <svg class="w-7 h-7 text-blue-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
        </div>
        <h2 class="text-lg font-semibold text-gray-800">{{ user.nom }} </h2>
        <div class="text-gray-500 text-sm">Mot de passe : <span class="font-mono">{{ user.motDePasse }}</span></div>
        <div class="mt-2 px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-600">
          {{ user.role === 'admin' ? 'Administrateur' : user.role.charAt(0).toUpperCase() + user.role.slice(1) }}
        </div>
      </div>
    </div>
  </div>
</template>