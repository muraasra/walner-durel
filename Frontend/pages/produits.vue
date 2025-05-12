<script setup lang="ts">
import creer_produit_modal from "@/components/produits/creer_produit_modal.vue";
import produit_card from "@/components/produits/produit_card.vue"; 

import type { Produit } from "~/types";

// Charge les produits depuis l'API Django
const { data: produits, refresh } = await useApi<Produit[]>("http://127.0.0.1:8000/api/produits/");

// Fonction pour ajouter un produit après création
async function ajouterProduit(product: Partial<Produit>) {
    const { data, error } = await useApi<Produit>("http://127.0.0.1:8000/api/produits/", {
        method: 'POST',
        body: product,
    });

    if (!error.value && data.value) {
        produits.value?.push(data.value); 
    } else {
        console.error('Erreur lors de la création du produit', error.value);
    }
}

// * Fonction pour modifier un produit
async function editerProduit(updatedProduit: Produit) {
    const { data, error } = await useApi<Produit>(
        `http://127.0.0.1:8000/api/produits/${updatedProduit.id}/`,
        {
            method: 'PATCH', 
            body: JSON.parse(JSON.stringify(updatedProduit)),
        }
    );

    if (!error.value && data.value) {
        // Met à jour dans la liste locale
        const index = produits.value?.findIndex((p) => p.id === data.value.id);
        if (index !== undefined && index !== -1) {
            produits.value[index] = data.value;
        }
    } else {
        console.error("Erreur lors de la mise à jour du produit", error.value);
    }
}

// * Fonction pour supprimer un produit
async function supprimerProduit(deletedProduit: Produit) {
    const { error } = await useApi(
        `http://127.0.0.1:8000/api/produits/${deletedProduit.id}/`,
        {
            method: 'DELETE',
        }
    );

    if (!error.value) {
        const index = produits.value?.findIndex((p) => p.id === deletedProduit.id);
        if (index !== undefined && index !== -1) {
            produits.value?.splice(index, 1);
        }
    } else {
        console.error("Erreur lors de la suppression du produit", error.value);
    }
}


</script>

<template>
  <section class="mt-5 px-6">
    <div class="flex items-center gap-x-4 justify-between">
      <h2 class="text-xl md:text-3xl font-bold">Produits</h2>
      <creer_produit_modal @creer-produit="ajouterProduit" />
    </div>

    <div
      class="mt-7 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-5 gap-y-6"
    >
      <produit_card
        v-for="produit in produits"
        :key="produit.id"
        :product="produit"
        @editer-produit="editerProduit"

        @delete-product="supprimerProduit"

      />
    </div>
  </section>
</template>
