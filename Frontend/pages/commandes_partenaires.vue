<script setup lang="ts">
import { ref, computed } from "vue";
import table_commandes_partenaires from "@/components/table_commandes_partenaires.vue";

// Simule les commandes récupérées depuis `facturation.vue`
const commandes = ref([
  {
    id: 1,
    date: "2025-03-13",
    partenaire: "Boutique A",
    total: 200000,
    verse: 50000,
    reste: 150000,
    produits: ["Produit 1", "Produit 2"],
  },
  {
    id: 2,
    date: "2025-03-12",
    partenaire: "Boutique B",
    total: 100000,
    verse: 20000,
    reste: 80000,
    produits: ["Produit 3", "Produit 4"],
  },
]);

// Calcul des totaux
const totalGlobal = computed(() => commandes.value.reduce((sum, cmd) => sum + cmd.total, 0));
const totalVerse = computed(() => commandes.value.reduce((sum, cmd) => sum + cmd.verse, 0));
const totalReste = computed(() => commandes.value.reduce((sum, cmd) => sum + cmd.reste, 0));
</script>

<template>
  <section class="mt-5 px-6">
    <h2 class="text-xl md:text-3xl font-bold text-blue-400">Listes des Commandes des Partenaires</h2>

    <!-- Résumé des montants -->
    <div class="mt-5 flex flex-col md:flex-row gap-4">
      <div class="p-4 border rounded bg-gray-100">
        <p class="text-lg font-semibold">Montant Total</p>
        <p class="text-xl font-bold text-blue-500">{{ totalGlobal }} FCFA</p>
      </div>
      <div class="p-4 border rounded bg-gray-100">
        <p class="text-lg font-semibold">Déjà Versé</p>
        <p class="text-xl font-bold text-green-500">{{ totalVerse }} FCFA</p>
      </div>
      <div class="p-4 border rounded bg-gray-100">
        <p class="text-lg font-semibold">Reste à Verser</p>
        <p class="text-xl font-bold text-red-500">{{ totalReste }} FCFA</p>
      </div>
    </div>

    <!-- Table des commandes -->
    <div class="mt-7 w-full">
      <table_commandes_partenaires :commandes="commandes" />
    </div>
  </section>
</template>
