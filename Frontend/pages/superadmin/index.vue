<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useApi } from '@/stores/useApi';
import type { Produit } from '~/types';

const produits = ref<Produit[] | null>(null);
const produitsEnStock = ref(0);

onMounted(async () => {
  const { data, error } = await useApi<Produit[]>("http://127.0.0.1:8000/api/produits/");
  if (!error.value && data.value) {
    produits.value = data.value;
    produitsEnStock.value = data.value.reduce((acc, prod) => acc + (prod.quantite ?? 0), 0);
  } else {
    produitsEnStock.value = 0;
  }
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="bg-white rounded-2xl shadow-xl p-10 max-w-xl w-full text-center">
      <h1 class="text-3xl md:text-4xl font-extrabold mb-4 text-blue-600">
        Bienvenue sur le Dashboard<br>
        <span class="text-gray-800">Super Admin</span>
        <span class="block text-base font-normal text-gray-400 mt-2">
          Gestionnaire de stockage Walner Tech
        </span>
      </h1>
      <p class="mb-8 text-gray-600">
        Vous pouvez superviser l'ensemble de la plateforme ici.<br>
        Utilisez le menu à gauche pour accéder à toutes les fonctionnalités.
      </p>
      <!-- Widgets de stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

        <div class="bg-green-50 rounded-lg p-4 shadow flex flex-col items-center">
          <span class="text-2xl font-bold text-green-500">{{ produitsEnStock }}</span>
          <span class="text-gray-500">Produits en stock</span>
        </div>
      </div>
    </div>
  </div>
</template>