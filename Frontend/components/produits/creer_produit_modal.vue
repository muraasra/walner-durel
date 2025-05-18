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
});

// Computed pour vérifier si l'utilisateur est super-admin
const isSuperAdmin = computed(() => {
  console.log('User role:', userRole.value);
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

    emit("creer-produit", {
      ...event.data,
      actif: true,
      boutique: 1,
    });

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
          <!-- Afficher le champ prix d'achat uniquement pour les super-admin -->
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
          <UButton type="submit" color="blue">Créer le produit</UButton>
        </UForm>
      </div>
    </UModal>
  </div>
</template>
