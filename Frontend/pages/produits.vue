<script setup lang="ts">
import creer_produit_modal from "@/components/produits/creer_produit_modal.vue";
import produit_card from "@/components/produits/produit_card.vue"; 

import type { Produit } from "~/types";
import { useApi } from '../stores/useApi';
import { useNotification } from '~/types/useNotification';

const { success, error } = useNotification();

// Charge les produits depuis l'API Django
const { data: produits, refresh } = await useApi<Produit[]>("http://127.0.0.1:8000/api/produits/");

// Fonction pour ajouter un produit après création
async function ajouterProduit(product: Partial<Produit>) {
    // Check if product with same reference already exists
    if (produits.value && produits.value.some(p => p.reference === product.reference)) {
        error("Un produit avec cette référence existe déjà.");
        return;
    }

    const { data, error: apiError } = await useApi<Produit>("http://127.0.0.1:8000/api/produits/", {
        method: 'POST',
        body: product,
    });

    if (!apiError.value && data.value) {
        produits.value?.push(data.value); 
        // Sort the products in descending order after adding a new one
        produits.value?.sort((a, b) => b.id - a.id);
        success("Produit ajouté avec succès!");
    } else {
        console.error('Erreur lors de la création du produit', apiError.value);
        error(`Erreur lors de la création du produit: ${apiError.value?.message || 'Une erreur est survenue'}`);
    }
}

// * Fonction pour modifier un produit
async function editerProduit(updatedProduit: Produit) {
    try {
        // Préparer les données à envoyer
        const productData = { ...updatedProduit };
        
        // Si c'est un ordinateur, formater correctement les champs
        if (productData.category === 'ordinateur') {
            // Convertir les champs vides en null
            const computerFields = ['ram', 'stockage', 'processeur', 'marque', 'modele', 'systeme_exploitation'];
            computerFields.forEach(field => {
                productData[field] = productData[field]?.trim() || null;
            });
            
            // Convertir l'année en nombre ou null
            if (productData.annee) {
                try {
                    productData.annee = typeof productData.annee === 'string' 
                        ? parseInt(productData.annee) 
                        : productData.annee;
                } catch (e) {
                    productData.annee = null;
                }
            } else {
                productData.annee = null;
            }
        }

        console.log('Données envoyées pour modification:', productData); // Pour le débogage

        const { data, error } = await useApi<Produit>(
            `http://127.0.0.1:8000/api/produits/${productData.id}/`,
            {
                method: 'PATCH', 
                body: productData,
            }
        );

        if (!error.value && data.value) {
            // Met à jour dans la liste locale
            const index = produits.value?.findIndex((p) => p.id === data.value.id);
            if (index !== undefined && index !== -1) {
                produits.value[index] = data.value;
                // Sort the products in descending order after editing
                produits.value.sort((a, b) => b.id - a.id);
            }
            success("Produit modifié avec succès!");
        } else {
            console.error("Erreur lors de la mise à jour du produit", error.value);
            error(`Erreur lors de la modification du produit: ${error.value?.message || 'Une erreur est survenue'}`);
        }
    } catch (err) {
        console.error("Exception lors de la modification du produit:", err);
        error("Une erreur est survenue lors de la modification du produit");
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
            // Sort the products in descending order after deleting
            produits.value.sort((a, b) => b.id - a.id);
        }
    } else {
        console.error("Erreur lors de la suppression du produit", error.value);
    }
}

// Sort products in descending order by ID after initial fetch
if (produits.value) {
    produits.value.sort((a, b) => b.id - a.id);
}
</script>

<template>
  <section class="mt-5 px-6">
    <div class="flex items-center gap-x-4 justify-between">
      <h2 class="text-xl md:text-3xl font-bold text-blue-400">Produits</h2>
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
