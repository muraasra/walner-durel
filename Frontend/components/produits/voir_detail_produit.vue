<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

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
    stockage?: string;
    processeur?: string;
    annee?: string;
    marque?: string;
    modele?: string;
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

// const auth = useAuthStore()

// Computed pour vérifier si l'utilisateur est super-admin
const isSuperAdmin = computed(() => {
  console.log('User role:', userRole.value);
  return userRole.value === "superadmin";
});

const isOpen = ref(false);
</script>
<template>
    <div>
      <UButton variant="soft" @click="isOpen = true">
        <UIcon name="i-heroicons-question-mark-circle" class="size-5" />
      </UButton>
      <UModal v-model="isOpen">
        <!-- <img
          :src="product.productImage || '/img/placeholder.png'"
          :alt="product.nom"
          class="w-full h-[220px]"
        /> -->
        <div class="p-4">
          <h2 class="mb-1 font-bold text-xl md:text-2xl">
            {{ product.nom }}
          </h2>
          <UBadge class="mb-3" color="blue">
            {{ product.category }}
          </UBadge>
          <h4 class="text-blue-400 font-bold">Prix de vente: {{ product.prix }} XAF</h4>
          <h4 v-if="isSuperAdmin && product.prix_achat" class="text-green-600 font-bold">Prix d'achat: {{ product.prix_achat }} XAF</h4>
          <h4>Quantité: {{ product.quantite }}</h4>
          <h4>Référence: {{ product.reference }}</h4>
          <h4 class="mt-2 font-semibold">Description :</h4>
          <p>{{ product.description }}</p>

          <!-- Spécifications des ordinateurs -->
          <template v-if="product.category === 'ordinateur'">
            <h4 class="mt-4 font-semibold">Spécifications techniques :</h4>
            <div class="grid grid-cols-2 gap-2 mt-2">
              <div v-if="product.ram">
                <span class="font-medium">RAM :</span>
                <span>{{ product.ram }}</span>
              </div>
              <div v-if="product.stockage">
                <span class="font-medium">Stockage :</span>
                <span>{{ product.stockage }}</span>
              </div>
              <div v-if="product.processeur">
                <span class="font-medium">Processeur :</span>
                <span>{{ product.processeur }}</span>
              </div>
              <div v-if="product.annee">
                <span class="font-medium">Année :</span>
                <span>{{ product.annee }}</span>
              </div>
              <div v-if="product.marque">
                <span class="font-medium">Marque :</span>
                <span>{{ product.marque }}</span>
              </div>
              <div v-if="product.modele">
                <span class="font-medium">Modèle :</span>
                <span>{{ product.modele }}</span>
              </div>
              <div v-if="product.systeme_exploitation">
                <span class="font-medium">Système d'exploitation :</span>
                <span>{{ product.systeme_exploitation }}</span>
              </div>
            </div>
          </template>

          <h4 class="mt-2">Statut : <span :class="product.actif ? 'text-green-600' : 'text-red-600'">{{ product.actif ? 'Actif' : 'Inactif' }}</span></h4>
        </div>
      </UModal>
    </div>
  </template>
  