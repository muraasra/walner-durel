<script setup lang="ts">
import { z } from "zod";
import type { FormSubmitEvent } from "#ui/types";

const isOpen = ref(false);
const emit = defineEmits(["creer-produit"]);

const schema = z.object({
  nom: z.string().min(3, "Must be at least 3 characters"),
  prix: z.number(),
  category: z.string(),
  quantite: z.number(),
  description: z.string(),
});

type Schema = z.output<typeof schema>;

const state = ref({
  nom: "",
  prix: 0,
  category: "",
  quantite: 0,
  description: "",
});

async function onSubmit(event: FormSubmitEvent<Schema>) {
  emit("creer-produit", {
    ...event.data,
    reference: `REF-${Math.random().toString(36).substring(2, 9).toUpperCase()}`,
    actif: true,
    boutique: 1, // Tu peux modifier cette valeur selon ta logique
  });
  isOpen.value = false;
  state.value = {
    nom: "",
    prix: "",
    category: "",
    quantite: "",
    description: "",
  };
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
          <UFormGroup label="Prix" name="prix">
            <UInput type="number" v-model="state.prix" placeholder="Prix" color="blue"/>
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
            <UInput
              type="number"
              v-model="state.quantite"
              placeholder="Quantité"
              color="blue"
            />
          </UFormGroup>
          <UFormGroup label="Description" name="description">
            <UTextarea
              v-model="state.description"
              placeholder="Description du produit"
              color="blue"
            />
          </UFormGroup>
          <UButton type="submit" color="blue"> Soumettre </UButton>
        </UForm>
      </div>
    </UModal>
  </div>
</template>
