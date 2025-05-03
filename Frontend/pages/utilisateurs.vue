<script setup>
import { ref } from "vue";

// État du formulaire
const afficherFormulaire = ref(false);

// Liste des utilisateurs (exemple)
const utilisateurs = ref([
  { nom: "Dupont", prenom: "Jean", role: "admin" },
  { nom: "Mballa", prenom: "Alice", role: "utilisateur" },
]);

// Modèle pour un nouvel utilisateur
const nouvelUtilisateur = ref({
  nom: "",
  prenom: "",
  role: "utilisateur",
  motDePasse: "",
});

// Ajouter un utilisateur
const ajouterUtilisateur = () => {
  if (nouvelUtilisateur.value.nom && nouvelUtilisateur.value.prenom && nouvelUtilisateur.value.motDePasse) {
    utilisateurs.value.push({ 
      nom: nouvelUtilisateur.value.nom, 
      prenom: nouvelUtilisateur.value.prenom, 
      role: nouvelUtilisateur.value.role 
    });
    nouvelUtilisateur.value = { nom: "", prenom: "", role: "utilisateur", motDePasse: "" };
    afficherFormulaire.value = false;
  }
};

// Supprimer un utilisateur
const supprimerUtilisateur = (index) => {
  utilisateurs.value.splice(index, 1);
};
</script>


<template>
    <div class="mt-5 px-6">
      <!-- En-tête -->
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl md:text-3xl font-bold text-blue-400">Utilisateurs</h2>
        <button 
          @click="afficherFormulaire = !afficherFormulaire" 
          class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          + Ajouter
        </button>
      </div>
  
      <!-- Formulaire d'ajout d'utilisateur -->
      <div v-if="afficherFormulaire" class="bg-gray-100 p-4 rounded-md mb-4">
        <input  v-model="nouvelUtilisateur.nom" type="text" placeholder="Nom" class="border border-blue-400 p-2 w-full mb-2 ">
        <input v-model="nouvelUtilisateur.prenom" type="text" placeholder="Prénom" class="border border-blue-400 p-2 w-full mb-2" >
        <select v-model="nouvelUtilisateur.role" class="border border-blue-400 p-2 w-full mb-2">
          <option value="admin">Admin</option>
          <option value="utilisateur">Utilisateur</option>
        </select>
        <input v-model="nouvelUtilisateur.motDePasse" type="password" placeholder="Mot de passe" class="border border-blue-400 p-2 w-full mb-2">
        <button @click="ajouterUtilisateur" class="px-4 py-2 bg-blue-400 text-white rounded-md hover:bg-blue-600">
          Ajouter l'utilisateur
        </button>
      </div>
  
      <!-- Liste des utilisateurs -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="(user, index) in utilisateurs" :key="index" class="p-4 bg-white shadow rounded-md">
          <h2 class="text-lg font-semibold">{{ user.nom }} {{ user.prenom }}</h2>
          <p class="text-gray-600">{{ user.role === 'admin' ? 'Administrateur' : 'Utilisateur' }}</p>
          <button @click="supprimerUtilisateur(index)" class="mt-2 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600">
            Supprimer
          </button>
        </div>
      </div>
    </div>
  </template>
  

  

  