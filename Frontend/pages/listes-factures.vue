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
const produitsFactures = ref<string[]>([]);

const totalGlobal = computed(() =>
  factures.value.reduce((acc, curr) => acc + (curr.total || 0), 0)
);

const totalVerse = computed(() =>
  factures.value.reduce((acc, curr) => acc + (curr.verse || 0), 0)
);

const totalReste = computed(() =>
  factures.value.reduce((acc, curr) => acc + (curr.reste || 0), 0)
);
const { data, error } = useApi('http://localhost:8000/api/factures/', {
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
      reste: facture.reste ?? 0
    }))
  : [];

console.log("Factures récupérées :", data.value);

const voirFacture = async (facture: Facture) => {
  // Logique pour afficher les détails de la facture
  factureSelectionnee.value = facture;
  showModal.value = true;

  const endpoint =  
    facture.type === "partenaire"
      ? `http://localhost:8000/api/commandes-partenaire/?facture=${facture.id}`
      : `http://localhost:8000/api/commandes-client/?facture=${facture.id}`;

  const { data, error } = useApi(endpoint, {
    method: 'GET',
    server: false
  });
  produitsFactures.value = (data.value as { produit: string }[]).map(cmd => cmd.produit)
};

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
        <table_factures :factures="factures" @voir="voirFacture"/>
      </div>

      <UModal v-model="showModal" :title="'Facture '+factureSelectionnee?.numero" :width="'80%'">
  <div v-if="factureSelectionnee" class="p-6 space-y-4">
    
    <!-- En-tête de la facture -->
    <div class="text-center">
      <h2 class="text-2xl font-bold">Facture #{{ factureSelectionnee.numero }}</h2>
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
            <th class="border px-4 py-2">Product</th>
            <th class="border px-4 py-2">Price</th>
            <th class="border px-4 py-2">Qty</th>
            <th class="border px-4 py-2">Subtotal</th>
          </tr>
        </thead>
        <tbody>
         
          <tr v-for="(prod, index) in produitsFactures" :key="index">
            <td class="border px-4 py-2 capitalize">{{ prod.nom }}</td>
            <td class="border px-4 py-2">{{ prod.prix.toFixed(2) }} Fcfa</td>
            <td class="border px-4 py-2">{{  }}</td>
            <td class="border px-4 py-2">{{ (prod.prix * prod.qte).toFixed(2) }} Fcfa</td>
          </tr>
        </tbody>
      </table>
    </div>
    <pre>{{ produitsFactures }}</pre>


    <!-- Totaux -->
    <div class="text-right text-sm space-y-1">
      <p><strong>Total excl. tax :</strong> {{ factureSelectionnee.total.toFixed(2) }} Fcfa</p>
      <p><strong>VAT (20%) :</strong> {{ (factureSelectionnee.total * 0.20).toFixed(2) }} Fcfa</p>
      <p class="text-xl font-bold text-red-500">
        Total incl. tax : {{ (factureSelectionnee.total * 1.20).toFixed(2) }} Fcfa
      </p>
    </div>
  </div>
</UModal>

    </section>
  </template>
  

