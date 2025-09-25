<script setup lang="ts">
import { z } from "zod";
import type { FormSubmitEvent } from "#ui/types";
import { useAuthStore } from '@/stores/auth'
import { useNotification } from '~/types/useNotification';

// const auth = useAuthStore()
const { success, error } = useNotification();

const isOpen = ref(false);
const emit = defineEmits(["creer-produit"]);

const user = ref(null);

if (process.client) {
  const userData = localStorage.getItem('user');
  if (userData) {
    user.value = JSON.parse(userData);
  }
}

const userRole = computed(() => user.value?.role || "user");

const schema = z.object({
  nom: z.string().min(3, "Must be at least 3 characters"),
  reference: z.string().min(1, "La référence est requise"),
  prix: z.number(),
  prix_achat: z.number().optional(),
  category: z.string(),
  quantite: z.number(),
  description: z.string(),
  // Champs spécifiques pour les ordinateurs
  ram: z.string().optional(),
  stockage: z.string().optional(),
  processeur: z.string().optional(),
  annee: z.string().optional(),
  marque: z.string().optional(),
  modele: z.string().optional(),
  systeme_exploitation: z.string().optional(),
});

type Schema = z.output<typeof schema>;

const state = ref({
  nom: "",
  reference: "",
  prix: 0,
  prix_achat: 0,
  category: "",
  quantite: 0,
  description: "",
  // Champs spécifiques pour les ordinateurs
  ram: "",
  stockage: "",
  processeur: "",
  annee: "",
  marque: "",
  modele: "",
  systeme_exploitation: "",
});

// Computed pour vérifier si l'utilisateur est superadmin
const isSuperAdmin = computed(() => {
  return userRole.value === "superadmin";
});

async function onSubmit(event: FormSubmitEvent<Schema>) {
  try {
    if (!event.data.nom) {
      error("Le nom du produit est requis");
      return;
    }
    if (!event.data.prix || event.data.prix <= 0) {
      error("Le prix de vente doit être supérieur à 0");
      return;
    }
    if (isSuperAdmin.value && event.data.prix_achat && event.data.prix_achat <= 0) {
      error("Le prix d'achat doit être supérieur à 0");
      return;
    }
    if (!event.data.category) {
      error("La catégorie est requise");
      return;
    }
    if (!event.data.quantite || event.data.quantite < 0) {
      error("La quantité doit être positive ou nulle");
      return;
    }
    if (!event.data.description) {
      error("La description est requise");
      return;
    }
    if (!event.data.reference) {
      error("La référence est requise");
      return;
    }

    // Préparer les données à envoyer
    const productData = {
      ...event.data,
      actif: true,
      boutique: 1,
    };

    // Si c'est un ordinateur, s'assurer que tous les champs sont présents et correctement formatés
    if (event.data.category === 'ordinateur') {
      // Convertir les champs vides en null
      const computerFields = ['ram', 'stockage', 'processeur', 'annee', 'marque', 'modele', 'systeme_exploitation'];
      computerFields.forEach(field => {
        productData[field] = event.data[field]?.trim() || null;
      });

      // Convertir l'année en nombre si elle n'est pas vide
      if (productData.annee) {
        try {
          productData.annee = parseInt(productData.annee);
        } catch (e) {
          productData.annee = null;
        }
      }
    }

    console.log('Données envoyées:', productData); // Pour le débogage
    emit("creer-produit", productData);

    success("Produit créé avec succès!");
    isOpen.value = false;
    state.value = {
      nom: "",
      reference: "",
      prix: 0,
      prix_achat: 0,
      category: "",
      quantite: 0,
      description: "",
      // Champs spécifiques pour les ordinateurs
      ram: "",
      stockage: "",
      processeur: "",
      annee: "",
      marque: "",
      modele: "",
      systeme_exploitation: "",
    };
  } catch (err) {
    console.error("Erreur lors de la création du produit:", err);
    error("Une erreur est survenue lors de la création du produit");
  }
}
</script>

<template>
  <div>
    <UButton color="blue" label="Ajouter un nouveau produit" @click="isOpen = true" />
    <UModal v-model="isOpen">
      <h3 class="text-center mt-4">Creer un nouveau produit</h3>
      <div class="p-4">
        <UForm
          :schema="schema"
          :state="state"
          class="space-y-4"
          @submit="onSubmit"
        >
          <UFormGroup label="Nom du produit" name="nom">
            <UInput v-model="state.nom" placeholder="Nom du produit" color="blue"/>
          </UFormGroup>
          <UFormGroup label="Référence" name="reference">
            <UInput v-model="state.reference" placeholder="Référence du produit" color="blue"/>
          </UFormGroup>
          <UFormGroup label="Prix de vente" name="prix">
            <UInput type="number" v-model="state.prix" placeholder="Prix de vente" color="blue"/>
          </UFormGroup>
          <!-- Afficher le champ prix d'achat uniquement pour les superadmin -->
          <UFormGroup v-if="isSuperAdmin" label="Prix d'achat" name="prix_achat">
            <UInput type="number" v-model="state.prix_achat" placeholder="Prix d'achat" color="blue"/>
          </UFormGroup>
          <UFormGroup label="Categorie" name="category">
            <USelect
              v-model="state.category"
              :options="[
                { value: 'telephone', label: 'Téléphone' },
                { value: 'ordinateur', label: 'Ordinateur' },
                { value: 'accessoire', label: 'Accessoire' },
                { value: 'ecran', label: 'Écran' },
                { value: 'imprimante', label: 'Imprimante' },
                { value: 'tablette', label: 'Tablette' },
                { value: 'casque', label: 'Casque' },
                { value: 'clavier', label: 'Clavier' },
                { value: 'souris', label: 'Souris' },
                { value: 'modem', label: 'Modem' },
                { value: 'disquedur', label: 'Disque dur' },
                { value: 'cleusb', label: 'Clé USB' },
                { value: 'autre', label: 'Autre' },
              ]"
              placeholder="Sélectionner une catégorie"
              color="blue"
            />
          </UFormGroup>
          <UFormGroup label="Quantité" name="quantite">
            <UInput type="number" v-model="state.quantite" placeholder="Quantité" color="blue"/>
          </UFormGroup>
          <UFormGroup label="Description" name="description">
            <UTextarea v-model="state.description" placeholder="Description du produit" color="blue"/>
          </UFormGroup>

          <!-- Champs spécifiques pour les ordinateurs -->
          <template v-if="state.category === 'ordinateur'">
            <UFormGroup label="RAM" name="ram">
              <UInput v-model="state.ram" placeholder="Ex: 8GB DDR4" color="blue"/>
            </UFormGroup>
            <UFormGroup label="Stockage" name="stockage">
              <UInput v-model="state.stockage" placeholder="Ex: SSD 256GB" color="blue"/>
            </UFormGroup>
            <UFormGroup label="Processeur" name="processeur">
              <UInput v-model="state.processeur" placeholder="Ex: Intel Core i5" color="blue"/>
            </UFormGroup>
            <UFormGroup label="Année" name="annee">
              <UInput v-model="state.annee" placeholder="Ex: 2023" color="blue"/>
            </UFormGroup>
            <UFormGroup label="Marque" name="marque">
              <UInput v-model="state.marque" placeholder="Ex: Dell" color="blue"/>
            </UFormGroup>
            <UFormGroup label="Modèle" name="modele">
              <UInput v-model="state.modele" placeholder="Ex: Latitude 5420" color="blue"/>
            </UFormGroup>
            <UFormGroup label="Système d'exploitation" name="systeme_exploitation">
              <UInput v-model="state.systeme_exploitation" placeholder="Ex: Windows 11" color="blue"/>
            </UFormGroup>
          </template>

          <UButton type="submit" color="blue">Créer le produit</UButton>
        </UForm>
      </div>
    </UModal>
  </div>
</template>
