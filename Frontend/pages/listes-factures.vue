<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import table_factures from '@/components/table_factures.vue';
import { useApi } from '../stores/useApi';

interface Facture {
  id: number;
  numero: string;
  date: string;
  nom: string;
  total: number;
  verse: number;
  reste: number;
  type: string;
  status: string;
}

interface ProduitFacture {
  nom: string;
  prix: number;
  quantite: number;
}

const factures = ref<Facture[]>([]);
const factureSelectionnee = ref<Facture | null>(null);
const showModal = ref(false);

const produitsFactures = ref<ProduitFacture[]>([]);

const totalGlobal = computed(() =>
  factures.value.reduce((acc, curr) => acc + (curr.total || 0), 0)
);

const totalVerse = computed(() =>
  factures.value.reduce((acc, curr) => acc + (curr.verse || 0), 0)
);

const totalReste = computed(() =>
  factures.value.reduce((acc, curr) => acc + (curr.reste || 0), 0)
);

// Pour le versement
const facturePourVersement = ref<Facture | null>(null);
const showVersementModal = ref(false);
const payment = ref<number>(0);
const errorMessage = ref<string | null>(null);

// --- Chargement des factures ---
async function loadFactures() {
  const { data, error } = await useApi('http://127.0.0.1:8000/api/factures/', { method: 'GET' });
  if (error.value) {
    console.error("Erreur API :", error.value);
    factures.value = [];
    return;
  }
  factures.value = Array.isArray(data.value)
    ? data.value.map(facture => {
        const verse = facture.total !== undefined && facture.reste !== undefined
          ? facture.total - facture.reste
          : getVersementPourFacture(facture.id);
        return {
          id: facture.id,
          numero: facture.numero,
          type: facture.type,
          status: facture.status,
          date: facture.created_at ? facture.created_at : 'Date inconnue', // Garde la date complète avec l'heure
          nom: facture.nom,
          total: facture.total ?? 0,
          verse,
          reste: facture.reste !== undefined ? facture.reste : (facture.total ?? 0) - verse,
        }
      }).sort((a, b) => {
        // Tri par date et heure décroissante
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return dateB.getTime() - dateA.getTime();
      })
    : [];
}

// --- Voir une facture ---
async function voirFacture(facture: Facture) {
  factureSelectionnee.value = facture;
  showModal.value = true;

  const endpoint =
    facture.type === "partenaire"
      ? `http://127.0.0.1:8000/api/commandes-partenaire/?facture=${facture.id}`
      : `http://127.0.0.1:8000/api/commandes-client/?facture=${facture.id}`;

  const { data, error } = await useApi(endpoint, { method: 'GET' });
  if (error.value) {
    produitsFactures.value = [];
    return;
  }
  produitsFactures.value = Array.isArray(data.value)
    ? data.value.map((cmd: any) => ({
        nom: cmd.produit?.nom || cmd.produit || 'Produit inconnu',
        prix: cmd.prix_unitaire_fcfa ?? cmd.prix ?? 0,
        quantite: cmd.quantite ?? 0
      }))
    : [];
}

// --- Gérer le versement ---
function ajouterVersement(facture: Facture) {
  facturePourVersement.value = facture;
  payment.value = 0;
  errorMessage.value = null;
  showVersementModal.value = true;
}

async function validerVersement() {
  if (!facturePourVersement.value) return;
  if (payment.value <= 0) {
    errorMessage.value = 'Entrez un montant positif.';
    return;
  }
  if (payment.value > facturePourVersement.value.reste) {
    errorMessage.value = 'Le montant du versement ne peux depasser le reste a payer.';
    return;
  }
  errorMessage.value = null;

  // 1. Met à jour le localStorage
  setVersement(facturePourVersement.value.id, payment.value);

  // 2. Calcule le nouveau reste et statut
  const nouveauReste = facturePourVersement.value.total - getVersementPourFacture(facturePourVersement.value.id);
  const nouveauStatut = nouveauReste === 0 ? 'payé' : 'encours';

  // 3. Met à jour le backend
  await useApi(`http://127.0.0.1:8000/api/factures/${facturePourVersement.value.id}/`, {
    method: 'PATCH',
    body: JSON.stringify({
      type: facturePourVersement.value.type,
      nom: facturePourVersement.value.nom,
      numero: facturePourVersement.value.numero,
      total: facturePourVersement.value.total,
      reste: nouveauReste,
      status: nouveauStatut,
      created_by: 1, // adapte selon ton contexte
      boutique: 1    // adapte selon ton contexte
    })
  });

  await loadFactures();
  showVersementModal.value = false;
}

function getVersements() {
  return JSON.parse(localStorage.getItem('versements') || '{}');
}

function setVersement(factureId: number, montant: number) {
  const versements = getVersements();
  versements[factureId] = (versements[factureId] || 0) + montant;
  localStorage.setItem('versements', JSON.stringify(versements));
}

function getVersementPourFacture(factureId: number) {
  const versements = getVersements();
  return versements[factureId] || 0;
}

onMounted(() => {
  loadFactures();
});
</script>

<template>
  <section class="mt-5 px-6">
    <h2 class="text-xl md:text-3xl font-bold text-blue-400">Listes des Factures</h2>

    <!-- Résumé des montants -->
    <div class="mt-5 flex flex-col md:flex-row gap-4">
      <div class="p-4 border rounded bg-gray-100">
        <p class="text-lg font-semibold">Montant Total</p>
        <p class="text-xl font-bold text-blue-500">{{ totalGlobal }} FCFA</p>
      </div>
      <div class="p-4 border rounded bg-gray-100">
        <p class="text-lg font-semibold">Déjà Versé</p>
        <p class="text-xl font-bold text-green-500">{{ totalVerse }} FCFA</p>
      </div>
      <div class="p-4 border rounded bg-gray-100">
        <p class="text-lg font-semibold">Reste à Verser</p>
        <p class="text-xl font-bold text-red-500">{{ totalReste }} FCFA</p>
      </div>
    </div>

    <!-- Table des Factures -->
    <div class="mt-7 w-full">
      <table_factures
        :factures="factures"
        @voir="voirFacture"
        @versement="ajouterVersement"
      />
    </div>

    <!-- Modal Voir Facture -->
    <UModal v-model="showModal" :title="'Facture ' + factureSelectionnee?.numero" :width="'80%'">
      <div v-if="factureSelectionnee" class="p-6 space-y-4">
        <div class="text-center">
          <h2 class="text-2xl font-bold text-blue-400">Facture {{ factureSelectionnee.numero }}</h2>
        </div>
        <div class="text-sm space-y-1">
          <p><strong>Date :</strong> {{ new Date(factureSelectionnee.date).toLocaleString('fr-FR', {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'}).replace(',', '') }}</p>
      
          <p><strong>Client :</strong> {{ factureSelectionnee.nom }}</p>
        </div>
        <hr />
        <div class="overflow-x-auto">
          <table class="w-full table-auto border-collapse">
            <thead class="bg-gray-100">
              <tr class="text-left">
                <th class="border px-4 py-2">Produit(s)</th>
                <th class="border px-4 py-2">Prix</th>
                <th class="border px-4 py-2">Quantité</th>
                <th class="border px-4 py-2">Sous-total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(prod, index) in produitsFactures" :key="index">
                <td class="border px-4 py-2 capitalize">{{ prod.nom }}</td>
                <td class="border px-4 py-2">{{ prod.prix.toFixed(2) }} Fcfa</td>
                <td class="border px-4 py-2">{{ prod.quantite }}</td>
                <td class="border px-4 py-2">{{ (prod.prix * prod.quantite).toFixed(2) }} Fcfa</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="text-right text-sm space-y-1">
          <p class="text-xl font-bold text-red-500">
            Total :  {{ (factureSelectionnee.total).toFixed(2) }} Fcfa
          </p>
          <p class="text-xl font-bold text-green-500">
            Reste a payer :  {{ (factureSelectionnee.reste).toFixed(2) }} Fcfa
          </p>
        </div>
      </div>
    </UModal>

    <!-- Modal Versement -->
    <UModal v-model="showVersementModal" title="Ajouter un versement">
      <div v-if="facturePourVersement" class="space-y-4 p-4">
        <div class="text-center">
          <h3 class="text-lg font-bold text-blue-500">Facture n° {{ facturePourVersement.numero }}</h3>
          <p class="text-gray-600">Client : {{ facturePourVersement.nom }}</p>
          <p class="text-gray-600">Reste a payé : <span class="font-bold text-red-500">{{ facturePourVersement.reste }} FCFA</span></p>
        </div>
        <div>
          <label class="block mb-1 font-semibold">Montant à verser</label>
          <input
            v-model="payment"
            type="number"
            min="1"
            :max="facturePourVersement.reste"
            placeholder="Montant à verser"
            class="border rounded px-3 py-2 w-full focus:ring focus:border-blue-400"
          />
          <div v-if="errorMessage" class="text-red-500 mt-1">{{ errorMessage }}</div>
        </div>
        <div class="flex justify-end gap-2 mt-4">
          <button @click="validerVersement" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Valider</button>
          <button @click="showVersementModal = false" class="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400">Annuler</button>
        </div>
      </div>
    </UModal>
  </section>
</template>
  

