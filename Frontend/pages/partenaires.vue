<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useApi } from "../stores/useApi";

// Typage du partenaire
interface Partenaire {
  id: number | string;
  nomPartenaire: string;
  prenomPartenaire: string;
  telephone: number;
  status: string; // Ce champ sera calculé en fonction des factures
  boutique: boolean;
  localisationBoutique: string;
  dateAdhesion: string;
}

interface Facture {
  id: number;
  numero: string;
  date: string;
  nom: string; // Le nom du client/partenaire
  total: number;
  verse: number;
  reste: number;
  type: string;
  status: string; // Statut de la facture individuelle ('payé', 'encours', etc.)
  // created_by: number;
  // boutique: number;
}

// Liste des partenaires
const partenaires = ref<Partenaire[]>([]);
// Liste de toutes les factures (pour le calcul du statut partenaire)
const toutesFactures = ref<Facture[]>([]);

// Charger les partenaires ET les factures depuis l'API
async function chargerDonnees() {
  console.log('Chargement des données partenaires et factures...');
  // 1. Charger les partenaires
  const { data: partenairesData, error: partenairesError } = await useApi("http://127.0.0.1:8000/api/partenaires/", {
    method: "GET",
    server: false,
  });

  if (partenairesError.value) {
    console.error("Erreur API Partenaires :", partenairesError.value);
    partenaires.value = [];
    toutesFactures.value = []; // Clear factures as well on partner error
    return;
  }

  const partenairesList = Array.isArray(partenairesData.value)
    ? partenairesData.value.map(p => ({
        id: p.id,
        nomPartenaire: p.nom,
        prenomPartenaire: p.prenom,
        telephone: p.telephone,
        // Le statut sera calculé plus tard
        status: "", // Initialise avec une chaîne vide
        boutique: !!p.boutique,
        localisationBoutique: p.localisation,
        dateAdhesion: p.dateadhesion,
      }))
    : [];
    console.log('Partenaires chargés:', partenairesList);

  // 2. Charger toutes les factures
  const { data: facturesData, error: facturesError } = await useApi('http://127.0.0.1:8000/api/factures/', { method: 'GET', server: false });

  if (facturesError.value) {
    console.error("Erreur API Factures :", facturesError.value);
    // Continuer avec la liste des partenaires même si les factures échouent
     partenaires.value = partenairesList.map(p => ({
         ...p,
         status: "Erreur Factures" // Indique qu'il y a eu une erreur pour les factures
     }));
    toutesFactures.value = [];
    return;
  }

  toutesFactures.value = Array.isArray(facturesData.value) ? facturesData.value : [];
   console.log('Factures chargées:', toutesFactures.value);

  // 3. Calculer le statut pour chaque partenaire basé sur les factures
  partenaires.value = partenairesList.map(partenaire => {
    // Préparer les parties du nom du partenaire pour la comparaison
    const nomPartenaireLower = partenaire.nomPartenaire.trim().toLowerCase();
    const prenomPartenaireLower = partenaire.prenomPartenaire.trim().toLowerCase();
     console.log(`Traitement partenaire ${partenaire.nomPartenaire} ${partenaire.prenomPartenaire}. Nom préparé: ${nomPartenaireLower}, Prénom préparé: ${prenomPartenaireLower}`);

    const facturesPartenaire = toutesFactures.value.filter(facture => {
        const isPartnerType = facture.type === 'partenaire';
        // Préparer le nom de la facture pour la comparaison
        const factureNomPrepare = facture.nom ? facture.nom.trim().toLowerCase() : ''; // Gérer le cas où facture.nom est null/undefined

         // Nouvelle logique de correspondance: vérifier si les deux parties du nom du partenaire sont incluses dans le nom de la facture, indépendamment de l\'ordre.
        const nomPresent = nomPartenaireLower.length > 0 && factureNomPrepare.includes(nomPartenaireLower);
        const prenomPresent = prenomPartenaireLower.length > 0 && factureNomPrepare.includes(prenomPartenaireLower);

        const nameMatches = isPartnerType && nomPresent && prenomPresent; // Correspond si c'est un partenaire ET que le nom ET le prénom sont présents

         console.log(`  - Vérification facture ${facture.numero}: Type='${facture.type}', Nom='${facture.nom}', Nom préparé facture='${factureNomPrepare}', Reste=${facture.reste}. IsPartnerType=${isPartnerType}, NomPresent=${nomPresent}, PrénomPresent=${prenomPresent}, NameMatches=${nameMatches}`);
        return nameMatches; // Le filtre retourne true si c'est une facture partenaire ET que les deux parties du nom correspondent
    });

    console.log(`  - Factures trouvées pour ${partenaire.nomPartenaire} ${partenaire.prenomPartenaire}:`, facturesPartenaire);

    // Déterminer le statut basé sur les factures trouvées
    let statutCalcule = "payé"; // Statut par défaut (si pas de factures ou toutes payées)

    if (facturesPartenaire.length > 0) {
        // Vérifie si au moins une facture a un reste > 0
        const hasDebt = facturesPartenaire.some(facture =>
            facture.reste !== undefined && facture.reste !== null && facture.reste > 0
        );

        if (hasDebt) {
            statutCalcule = "En cours"; // Si au moins une facture a de la dette
        } else {
            statutCalcule = "payé"; // Si toutes les factures ont reste <= 0
        }
    }
     console.log(`  - Statut calculé: ${statutCalcule}`);

     // Si aucune facture n'est trouvée, on considère le partenaire comme 'payé' par défaut.

    return {
      ...partenaire,
      status: statutCalcule,
    };
  });
   console.log('Liste finale des partenaires avec statuts:', partenaires.value);
}

onMounted(() => {
  // Appelle la nouvelle fonction de chargement qui gère partenaires et factures
  chargerDonnees();
});

// ⚙️ Ajout d'un partenaire
const showModal = ref(false);
const showEditModal = ref(false);
const partenaireToEdit = ref<Partenaire | null>(null);

const nouveauPartenaire = ref<Omit<Partenaire, 'id' | 'status'>>({
  nomPartenaire: "",
  prenomPartenaire: "",
  telephone: 0,
  // status: "paye", // Le statut n'est pas défini à l'ajout, il dépend des factures futures
  boutique: false,
  localisationBoutique: "",
  dateAdhesion: new Date().toISOString().split("T")[0],
});

const ajouterPartenaire = async () => {
    // Basic validation
    if (!nouveauPartenaire.value.nomPartenaire || !nouveauPartenaire.value.prenomPartenaire || !nouveauPartenaire.value.telephone) {
        // Handle validation error, e.g., show a notification
        console.error("Nom, prénom et téléphone sont requis.");
        return;
    }

  const { data, error } = await useApi("http://127.0.0.1:8000/api/partenaires/", {
    method: "POST",
    body: {
      nom: nouveauPartenaire.value.nomPartenaire,
      prenom: nouveauPartenaire.value.prenomPartenaire,
      telephone: nouveauPartenaire.value.telephone,
      localisation: nouveauPartenaire.value.localisationBoutique,
      // statut: nouveauPartenaire.value.status, // Ne pas envoyer le statut ici, il dépend des factures
      dateadhesion: nouveauPartenaire.value.dateAdhesion,
      boutique: nouveauPartenaire.value.boutique,
    },
    server: false,
  });

  if (!error.value) {
    // Après l'ajout, recharge toutes les données (partenaires et factures) pour mettre à jour la liste
    await chargerDonnees();
    showModal.value = false;
     // Reset form
    nouveauPartenaire.value = {
      nomPartenaire: "",
      prenomPartenaire: "",
      telephone: 0,
      boutique: false,
      localisationBoutique: "",
      dateAdhesion: new Date().toISOString().split("T")[0],
    };

  } else {
      console.error("Erreur lors de l'ajout du partenaire:", error.value);
      // Handle API error during add
  }
};

// ⚙️ Modifier un partenaire
const ouvrirModaleModification = (partenaire: Partenaire) => {
  // Créer une copie pour l'édition, mais sans modifier le statut calculé directement
  partenaireToEdit.value = {
      ...partenaire,
      // On ne copie pas le statut calculé, car il sera redéterminé après modification si nécessaire
      status: "", // Le statut affiché dans la modale n'est pas pertinent, ou tu peux afficher l'ancien statut si tu préfères
   };
  showEditModal.value = true;
};

const enregistrerModifications = async () => {
  if (!partenaireToEdit.value) return;

  // Préparer les données pour l'API (exclure le champ status qui n'est pas modifiable ici)
  const { id, status, ...dataToSend } = partenaireToEdit.value;

   // Basic validation before sending
    if (!dataToSend.nomPartenaire || !dataToSend.prenomPartenaire || !dataToSend.telephone) {
         console.error("Nom, prénom et téléphone sont requis pour la modification.");
        return;
    }

  const { data, error } = await useApi(`http://127.0.0.1:8000/api/partenaires/${id}/`, {
    method: "PUT", // ou 'PATCH' selon ton API
    body: {
        nom: dataToSend.nomPartenaire,
        prenom: dataToSend.prenomPartenaire,
        telephone: dataToSend.telephone,
        localisation: dataToSend.localisationBoutique,
        dateadhesion: dataToSend.dateAdhesion,
        boutique: dataToSend.boutique,
         // N'envoie pas le champ 'statut' ici
    },
    server: false,
  });

  if (!error.value) {
    // Après la modification, recharge toutes les données pour recalculer les statuts
    await chargerDonnees();
    showEditModal.value = false;
    partenaireToEdit.value = null; // Clear the edited partner
  } else {
       console.error("Erreur lors de la modification du partenaire:", error.value);
        // Handle API error during edit
  }
};

// Colonnes (utiliseront le champ status calculé)
const columns = [
  { key: "nomPartenaire", label: "Nom" },
  { key: "prenomPartenaire", label: "Prénom" },
  { key: "telephone", label: "Téléphone" },
  { key: "status", label: "Statut" },
  { key: "boutique", label: "Boutique" },
  { key: "localisationBoutique", label: "Localisation" },
  { key: "dateAdhesion", label: "Date d'adhésion" },
  { key: "actions", label: "Actions" },
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

        <!-- Colonne personnalisée pour "Statut" (utilise le statut calculé) -->
        <template #status-data="{ row }">
          <span class="px-2 py-1 rounded-lg text-white text-sm font-medium" :class="
            row.status === 'payé' ? 'bg-green-500' :
            row.status === 'En cours' ? 'bg-yellow-500' :
            'bg-red-500'
          ">
            {{ row.status }}
          </span>
        </template>

        <!-- Colonne personnalisée pour les actions -->
        <template #actions-data="{ row }">
          <UButton color="blue" @click="ouvrirModaleModification(row)">Modifier</UButton>
          <!-- Ajoute ici un bouton ou une action pour supprimer si nécessaire -->
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
        <UInput color="blue" variant="outline" v-model="nouveauPartenaire.telephone" placeholder="Téléphone" type="number"
          class="mb-2" />
        <UInput color="blue" variant="outline" v-model="nouveauPartenaire.localisationBoutique"
          placeholder="Localisation Boutique" class="mb-2" />
        <UCheckbox color="blue" variant="outline" v-model="nouveauPartenaire.boutique" label="Possède une boutique ?"
          class="mb-2" />
         <!-- Le champ dateAdhesion pourrait être un datepicker si tu veux -->
        <UInput color="blue" variant="outline" v-model="nouveauPartenaire.dateAdhesion" placeholder="Date d'adhésion (YYYY-MM-DD)" type="date"
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
        <UInput color="blue" variant="outline" v-model="partenaireToEdit.telephone" placeholder="Téléphone" type="number"
          class="mb-2" />
        <UInput color="blue" variant="outline" v-model="partenaireToEdit.localisationBoutique"
          placeholder="Localisation Boutique" class="mb-2" />
        <UCheckbox color="blue" variant="outline" v-model="partenaireToEdit.boutique" label="Possède une boutique ?"
          class="mb-2" />
         <!-- Le champ dateAdhesion pourrait être un datepicker si tu veux -->
         <UInput color="blue" variant="outline" v-model="partenaireToEdit.dateAdhesion" placeholder="Date d'adhésion (YYYY-MM-DD)" type="date"
            class="mb-2" />
        <UButton color="blue" @click="enregistrerModifications">Enregistrer</UButton>
        <UButton color="gray" variant="outline" class="ml-2" @click="showEditModal = false">Annuler</UButton>
      </div>
    </UModal>
  </div>
</template>