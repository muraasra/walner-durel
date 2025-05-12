<script setup lang="ts">
defineProps<{
  product: {
    id: number;
    reference: string;
    category: string;
    nom: string;
    description: string;
    quantite: number;
    prix: number;
    actif: boolean;
    boutique: number;
  };
}>();

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
          <h4 class="text-blue-400 font-bold">Prix: {{ product.prix }} XAF</h4>
          <h4>Quantité: {{ product.quantite }}</h4>
          <h4>Référence: {{ product.reference }}</h4>
          <h4 class="mt-2 font-semibold">Description :</h4>
          <p>{{ product.description }}</p>
          <h4 class="mt-2">Statut : <span :class="product.actif ? 'text-green-600' : 'text-red-600'">{{ product.actif ? 'Actif' : 'Inactif' }}</span></h4>
        </div>
      </UModal>
    </div>
  </template>
  