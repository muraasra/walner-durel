<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import table_factures from '@/components/table_factures.vue';

interface Facture {
  id: number;
  date: string;
  partenaire: string;
  total: number;
  verse: number;
  reste: number;
  produits: string[];
}

const factures = ref<Facture[]>([]);

const totalGlobal = computed(() =>
  factures.value.reduce((acc, curr) => acc + (curr.total || 0), 0)
);

const totalVerse = computed(() =>
  factures.value.reduce((acc, curr) => acc + (curr.verse || 0), 0)
);

const totalReste = computed(() =>
  factures.value.reduce((acc, curr) => acc + (curr.reste || 0), 0)
);

const fetchFactures = async () => {
  try {
    const response = await useApi('http://127.0.0.1:8000/api/factures-detaillees/');
    factures.value = response.data.map((facture: any) => ({
      id: facture.id,
      date: facture.date.split('T')[0],
      type: facture.destinataire,
      total: facture.total,
      verse: facture.verse,
      reste: facture.reste,
      produits: facture.produits,
    }));
  } catch (error) {
    console.error('Erreur de récupération des factures détaillées:', error);
  }
};

onMounted(fetchFactures);
</script>

<template>
    <section class="mt-5 px-6">
      <h2 class="text-xl md:text-3xl font-bold text-blue-400">Listes des Factures</h2>
  
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
  
      <!-- Table des Fatures -->
      <div class="mt-7 w-full">
        <table_factures :factures="factures" />
      </div>
    </section>
  </template>
  

