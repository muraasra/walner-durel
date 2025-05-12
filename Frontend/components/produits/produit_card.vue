<script setup lang="ts">
import editer_produit_modal from "./editer_produit_modal.vue";
import voir_detail_produit from "./voir_detail_produit.vue";

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
  
