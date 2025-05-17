<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import table_factures from '@/components/table_factures.vue';

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

const factures = ref<Facture[]>([]);
const factureSelectionnee = ref<Facture | null>(null);
const showModal = ref(false);

interface ProduitFacture {
  nom: string;
  prix: number;
  quantite: number;
}
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
const { data, error } = useApi('http://127.0.0.1:8000/api/factures/', {
    method: 'GET',
    server: false
});

if (error.value) {
    console.error("Erreur API :", error.value);
}
factures.value = Array.isArray(data.value)
  ? data.value.map(facture => ({
      id: facture.id,
      numero: facture.numero,
      type: facture.type,
      status: facture.status,
      date: facture.created_at ? facture.created_at.split('T')[0] : 'Date inconnue',
      nom: facture.nom ,
      total: facture.total ?? 0,
      verse: facture.verse ?? 0,  // Vérifiez si l'API retourne ce champ
      reste: (facture.total ?? 0) - (facture.verse ?? 0),
    }))
  : [];

console.log("Factures récupérées :", data.value);

const voirFacture = async (facture: Facture) => {
  // Logique pour afficher les détails de la facture
  factureSelectionnee.value = facture;
  showModal.value = true;

  const endpoint =  
    facture.type === "partenaire"
      ? `http://127.0.0.1:8000/api/commandes-partenaire/?facture=${facture.id}`
      : `http://127.0.0.1:8000/api/commandes-client/?facture=${facture.id}`;

  const { data, error } = useApi(endpoint, {
    method: 'GET',
    server: false
  });
  produitsFactures.value = (data.value as { produit: string }[]).map(cmd => ({
    nom: cmd.produit,
    prix: cmd.prix,
    quantite: cmd.quantite
  }));
};

const facturePourVersement = ref<Facture | null>(null);
const showVersementModal = ref(false);
const payment = ref<number>(0);
const errorMessage = ref<string | null>(null);

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
    errorMessage.value = 'Le montant dépasse le reste dû.';
    return;
  }
  errorMessage.value = null;
  // Appel API pour mettre à jour la facture
  await useApi(`http://127.0.0.1:8000/api/factures/${facturePourVersement.value.id}`, {
    method: 'POST',
    body: JSON.stringify({ montant: payment.value })
  });
  // Recharge la liste des factures
  // ... (refaire l'appel API pour rafraîchir factures)
  showVersementModal.value = false;
}

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
  
      <!-- Table des Fatures -->
      <div class="mt-7 w-full">
        <table_factures :factures="factures" @voir="voirFacture" @versement="ajouterVersement" />
      </div>

      <UModal v-model="showModal" :title="'Facture '+factureSelectionnee?.numero" :width="'80%'">
  <div v-if="factureSelectionnee" class="p-6 space-y-4">
    
    <!-- En-tête de la facture -->
    <div class="text-center">
      <h2 class="text-2xl font-bold text-blue-400">Facture {{ factureSelectionnee.numero }}</h2>
    </div>

    <!-- Informations client -->
    <div class="text-sm space-y-1">
      <p><strong>Date :</strong> {{ factureSelectionnee.date }}</p>
      <p><strong>Client :</strong> {{ factureSelectionnee.nom }}</p>
    </div>

    <hr />

    <!-- Tableau des produits -->
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
    <pre>{{ produitsFactures }}</pre>


    <!-- Totaux -->
    <div class="text-right text-sm space-y-1">
      <!-- <p><strong>Total excl. tax :</strong> {{ factureSelectionnee.total.toFixed(2) }} Fcfa</p>
      <p><strong>VAT (20%) :</strong> {{ (factureSelectionnee.total * 0.20).toFixed(2) }} Fcfa</p> -->
      <p class="text-xl font-bold text-red-500">
        Total :  {{ (factureSelectionnee.total).toFixed(2) }} Fcfa
      </p>
    </div>
  </div>
</UModal>

<UModal v-model="showVersementModal" title="Ajouter un versement">
  <div v-if="facturePourVersement">
    <p>Facture n° {{ facturePourVersement.numero }} (Reste dû : {{ facturePourVersement.reste }} FCFA)</p>
    <input v-model="payment" type="number" min="1" :max="facturePourVersement.reste" placeholder="Montant à verser" />
    <div v-if="errorMessage" class="text-red-500">{{ errorMessage }}</div>
    <button @click="validerVersement">Valider</button>
    <button @click="showVersementModal = false">Annuler</button>
  </div>
</UModal>

    </section>
  </template>
  

