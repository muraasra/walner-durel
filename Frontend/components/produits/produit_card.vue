<script setup lang="ts">
import editer_produit_modal from "./editer_produit_modal.vue";
import voir_detail_produit from "./voir_detail_produit.vue";
import { ref, computed } from 'vue';

defineProps<{
  product: {
    id: number;
    reference: string;
    category: string;
    nom: string;
    description: string;
    quantite: number;
    prix: number;
    prix_achat?: number;
    actif: boolean;
    boutique: number;
    // Champs spécifiques pour les ordinateurs
    ram?: string;
    disque_dur?: string;
    processeur?: string;
    generation?: string;
    carte_graphique?: string;
    systeme_exploitation?: string;
  };
}>();

const user = ref(null);

if (process.client) {
  const userData = localStorage.getItem('user');
  if (userData) {
    user.value = JSON.parse(userData);
  }
}

const userRole = computed(() => user.value?.role || "user");

// Computed pour vérifier si l'utilisateur est superadmin
const isSuperAdmin = computed(() => {
  return userRole.value === "superadmin";
});

const emit = defineEmits(["delete-product", "editer-produit"]);

const onDelete = (product: any) => emit("delete-product", product);
</script>
<template>
    <div
      class="w-full h-full shadow-lg border rounded-lg hover:shadow-md transition-all dark:border-gray-600 dark:shadow-gray-800"
    >
      <!-- <img
        :src="product.productImage || '/img/placeholder.png'"
        :alt="product.nom"
        class="h-[200px] w-full rounded-t-lg"
      /> -->
      <div class="px-4">
        <h2 class="mb-1 font-bold">{{ product.nom }}</h2>
        <UBadge size="sm" class="mb-3 bg-blue-400">
          {{ product.category }}
        </UBadge>
        <h4 class="text-blue-400">{{ product.prix }} XAF</h4>
        <h4 v-if="isSuperAdmin && product.prix_achat" class="text-green-600">Prix d'achat: {{ product.prix_achat }} XAF</h4>
        <h4 class="block">Quantité: {{ product.quantite }}</h4>
      </div>
      <div class="px-4 mt-4 mb-5 flex items-center gap-x-2">
        <voir_detail_produit :product="product" />
        <editer_produit_modal
          :product="product"
          @editer-produit="
            (product) => {
              emit('editer-produit', product);
            }
          "
        />
        <UButton variant="outline" color="red" @click="onDelete(product)">
          Supprimer
        </UButton>
      </div>
    </div>
  </template>
  
