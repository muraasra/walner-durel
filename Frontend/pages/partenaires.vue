<script setup lang="ts">
import { ref } from "vue";
import type { Partenaire } from "~/types";

const { data, error } = useApi('http://127.0.0.1:8000/api/partenaires/', {
  method: 'GET',
  server: false
});

if (error.value) {
  console.error("Erreur API :", error.value);
}

const partenaires = Array.isArray(data.value)
  ? data.value.map(p => ({
    id: p.id,
    nomPartenaire: p.nom,
    prenomPartenaire: p.prenom,
    telephone: p.telephone,
    status: p.statut,
    boutique: p.boutique ? true : false,
    localisationBoutique: p.localisation,
    dateAdhesion: p.dateadhesion,
  }))
  : [];


// État pour afficher/masquer la modale d'ajout
const showModal = ref(false);

// État pour afficher/masquer la modale de modification
const showEditModal = ref(false);

// Partenaire sélectionné pour modification
const partenaireToEdit = ref<Partenaire | null>(null);

// Modèle pour un nouveau partenaire
const nouveauPartenaire = ref<Partenaire>({
  id: "",
  nomPartenaire: "",
  prenomPartenaire: "",
  telephone: 0,
  status: "paye",
  boutique: false,
  localisationBoutique: "",
  dateAdhesion: new Date().toISOString().split("T")[0],
});

// Fonction pour ajouter un partenaire
const ajouterPartenaire = () => {
  nouveauPartenaire.value.id = String(partenaires.length + 1);
  // partenaires.push({ ...nouveauPartenaire.value });
  const { data, error } = useApi('http://127.0.0.1:8000/api/partenaires/', {
    method: 'POST',
    body: {
      nom: nouveauPartenaire.value.nomPartenaire,
      prenom: nouveauPartenaire.value.prenomPartenaire,
      telephone: nouveauPartenaire.value.telephone,
      localisation: nouveauPartenaire.value.localisationBoutique,
      statut: nouveauPartenaire.value.status,
      dateadhesion: nouveauPartenaire.value.dateAdhesion,
      boutique: nouveauPartenaire.value.boutique,
    },
    server: false
  });
  nouveauPartenaire.value = {
    id: "",
    nomPartenaire: "",
    prenomPartenaire: "",
    telephone: 0,
    status: "paye",
    boutique: false,
    localisationBoutique: "",
    dateAdhesion: new Date().toISOString(),
  };
  showModal.value = false;
};

// Fonction pour ouvrir la modale de modification
const ouvrirModaleModification = (partenaire: Partenaire) => {
  partenaireToEdit.value = { ...partenaire }; // Copier le partenaire sélectionné
  showEditModal.value = true; // Ouvrir la modale de modification
};

// Fonction pour enregistrer les modifications
const enregistrerModifications = () => {
  if (partenaireToEdit.value) { // Vérifier que partenaireToEdit n'est pas null
    const index = partenaires.findIndex((p) => p.id === partenaireToEdit.value?.id);
    if (index !== -1) {
      partenaires[index] = { ...partenaireToEdit.value }; // Mettre à jour le partenaire
    }
    showEditModal.value = false; // Fermer la modale
  }
};

// Colonnes de la table
const columns = [
  { key: "nomPartenaire", label: "Nom" },
  { key: "prenomPartenaire", label: "Prénom" },
  { key: "telephone", label: "Téléphone" },
  { key: "status", label: "Statut" },
  { key: "boutique", label: "Boutique" },
  { key: "localisationBoutique", label: "Localisation" },
  { key: "dateAdhesion", label: "Date d'adhésion" },
  { key: "actions", label: "Actions" }, // Nouvelle colonne pour les actions
];
</script>

<template>
  <div class="mt-5 px-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl md:text-3xl font-bold text-blue-400">Partenaires</h2>
      <UButton @click="showModal = true" color="blue"> + Ajouter Un Partenaire </UButton>
    </div>

    <!-- Tableau des partenaires -->
    <div class="bg-white shadow-md rounded-lg border p-4">
      <UTable :rows="partenaires" :columns="columns">
        <!-- Colonne personnalisée pour "Boutique" -->
        <template #boutique-data="{ row }">
          <span class="flex items-center gap-1" :class="row.boutique ? 'text-green-500' : 'text-red-500'">
            <UIcon v-if="row.boutique" name="i-heroicons-check-circle" class="w-5 h-5 text-green-500" />
            <UIcon v-else name="i-heroicons-x-circle" class="w-5 h-5 text-red-500" />
            {{ row.boutique ? "Oui" : "Non" }}
          </span>
        </template>

        <!-- Colonne personnalisée pour "Statut" -->
        <template #status-data="{ row }">
          <span class="px-2 py-1 rounded-lg text-white text-sm font-medium" :class="{
            'bg-green-500': row.status === 'paye',
            'bg-yellow-500': row.status === 'En cours de payement',
            'bg-red-500': row.status !== 'paye' && row.status !== 'En cours de payement',
          }">
            {{ row.status }}
          </span>
        </template>

        <!-- Colonne personnalisée pour les actions -->
        <template #actions-data="{ row }">
          <UButton color="blue" @click="ouvrirModaleModification(row)">Modifier</UButton>
        </template>
      </UTable>
    </div>

    <!-- Modale pour ajouter un partenaire -->
    <UModal v-model="showModal">
      <div class="p-5">
        <h2 class="text-lg font-bold mb-4 text-blue-400">Ajouter un Partenaire</h2>
        <UInput color="blue" variant="outline" v-model="nouveauPartenaire.nomPartenaire" placeholder="Nom"
          class="mb-2" />
        <UInput color="blue" variant="outline" v-model="nouveauPartenaire.prenomPartenaire" placeholder="Prénom"
          class="mb-2" />
        <UInput color="blue" variant="outline" v-model="nouveauPartenaire.telephone" placeholder="Téléphone"
          class="mb-2" />
        <UInput color="blue" variant="outline" v-model="nouveauPartenaire.localisationBoutique"
          placeholder="Localisation Boutique" class="mb-2" />
        <UCheckbox color="blue" variant="outline" v-model="nouveauPartenaire.boutique" label="Possède une boutique ?"
          class="mb-2" />
        <UButton color="blue" @click="ajouterPartenaire">Ajouter</UButton>
        <UButton color="gray" variant="outline" class="ml-2" @click="showModal = false">Annuler</UButton>
      </div>
    </UModal>

    <!-- Modale pour modifier un partenaire -->
    <UModal v-model="showEditModal">
      <div class="p-5" v-if="partenaireToEdit">
        <h2 class="text-lg font-bold mb-4 text-blue-400">Modifier un Partenaire</h2>
        <UInput color="blue" variant="outline" v-model="partenaireToEdit.nomPartenaire" placeholder="Nom"
          class="mb-2" />
        <UInput color="blue" variant="outline" v-model="partenaireToEdit.prenomPartenaire" placeholder="Prénom"
          class="mb-2" />
        <UInput color="blue" variant="outline" v-model="partenaireToEdit.telephone" placeholder="Téléphone"
          class="mb-2" />
        <UInput color="blue" variant="outline" v-model="partenaireToEdit.localisationBoutique"
          placeholder="Localisation Boutique" class="mb-2" />
        <UCheckbox color="blue" variant="outline" v-model="partenaireToEdit.boutique" label="Possède une boutique ?"
          class="mb-2" />
        <UButton color="blue" @click="enregistrerModifications">Enregistrer</UButton>
        <UButton color="gray" variant="outline" class="ml-2" @click="showEditModal = false">Annuler</UButton>
      </div>
    </UModal>
  </div>
</template>