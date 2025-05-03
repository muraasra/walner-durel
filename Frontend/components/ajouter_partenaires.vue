<script setup lang="ts">
import { ref, defineEmits } from "vue";
import type { Partenaire } from "~/types";

const emit = defineEmits(["close", "ajouterPartenaire"]);

// Modèle pour un nouveau partenaire
const nouveauPartenaire = ref<Partenaire>({
  id: "",
  nomPartenaire: "",
  prenomPartenaire: "",
  telephone: 0,
  status: "non payé",
  boutique: false,
  localisationBoutique: "",
  dateAdhesion: new Date().toISOString().split("T")[0],
});

const ajouter = () => {
  emit("ajouterPartenaire", { ...nouveauPartenaire.value });
  emit("close"); // Fermer la modale après ajout
};
</script>

<template>
  <UModal @close="emit('close')">
    <div class="p-5">
      <h2 class="text-lg font-bold mb-4 text-blue-400">Ajouter un Partenaire</h2>

      <UInput v-model="nouveauPartenaire.nomPartenaire" placeholder="Nom" class="mb-2" />
      <UInput v-model="nouveauPartenaire.prenomPartenaire" placeholder="Prénom" class="mb-2" />
      <UInput v-model="nouveauPartenaire.telephone" type="number" placeholder="Téléphone" class="mb-2" />
      <UInput v-model="nouveauPartenaire.localisationBoutique" placeholder="Localisation Boutique" class="mb-2" />

      <UCheckbox v-model="nouveauPartenaire.boutique" label="Possède une boutique ?" class="mb-2" />

      <UButton color="blue" @click="ajouter">Ajouter</UButton>
      <UButton color="gray" variant="outline" class="ml-2" @click="emit('close')">Annuler</UButton>
    </div>
  </UModal>
</template>
