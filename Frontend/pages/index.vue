<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import KpiCard from '@/components/KpiCard.vue';
import { useNotification } from '../types/useNotification';
import { useApi } from '../stores/useApi';

// --- Types ---
interface Product {
  id: number;
  reference: string;
  nomProduit: string;
  category: string;
  prix_achat: number;
  prix: number;
  description: string;
  quantiteTotale: number;
  statut: boolean;
  boutique: number;
}

interface Commande {
  id: number;
  facture: number;
  nom: string;
  prenom: string;
  quantite: number;
  telephone: string;
  produit: Product;
  prix_unitaire_fcfa: number;
  total: number;
}


interface FactureUI {
  id: number;
  type: string;
  nom: string;
  numero: string;
  total: number;
  verse: number;
  reste: number;
  status: string;
  date: string;
}

// --- States ---
const dateRange = ref('today');
const startDate = ref('');
const endDate = ref('');
const debts = ref<Debt[]>([]);
const factures = ref<FactureUI[]>([]);
const loading = ref(true);
const allFactures = ref<FactureUI[]>([]);

// --- API Data ---
const { data: produits } = await useApi<Product[]>('http://127.0.0.1:8000/api/produits/', { method: 'GET' });
const { data: commandesClient } = await useApi<Commande[]>('http://127.0.0.1:8000/api/commandes-client/', { method: 'GET' });
const { data: commandesPartenaires } = await useApi<Commande[]>('http://127.0.0.1:8000/api/commandes-partenaire/', { method: 'GET' });

// --- Computed ---
const computerCount = computed(() =>
  produits.value?.filter(p => p.category.toLowerCase() === 'ordinateur').length ?? 0
);

const phoneCount = computed(() =>
  produits.value?.filter(p => p.category.toLowerCase() === 'telephone').length ?? 0
);

const accessoryCount = computed(() => {
  const accessoryCategories = ['accessoire', 'clavier', 'cleusb', 'souris'];
  return produits.value?.filter(p =>
    accessoryCategories.includes(p.category.toLowerCase())
  ).length ?? 0;
});

const margeTotale = computed(() => {
  const allCommandes = [
    ...(commandesClient.value || []),
    ...(commandesPartenaires.value || [])
  ];
  return allCommandes.reduce((sum, ligne) => {
    const prixAchat = ligne.produit?.prix_achat ?? 0;
    const prixVente = ligne.prix_unitaire_fcfa ?? 0;
    const quantite = ligne.quantite ?? 0;
    return sum + (prixVente - prixAchat) * quantite;
  }, 0);
});

const totalDetteGlobale = computed(() =>
  allFactures.value.reduce((sum, f) => sum + (f.reste), 0)
);

const chiffreAffaireTotal = computed(() => {
  return allFactures.value.reduce((sum, f) => sum + f.total, 0);
});

const chiffreAffaireEncaisse = computed(() => {
  return allFactures.value.reduce((sum, f) => sum + (f.total - f.reste), 0);
});

const chiffreAffaireDette = computed(() => {
  return allFactures.value.reduce((sum, f) => sum + f.reste, 0);
});

// --- Méthodes utilitaires ---
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF' }).format(value);
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR');
}

// --- Chargement des factures ---
async function loadFacturesJour() {
  try {
    loading.value = true;
    const today = new Date().toISOString().split('T')[0];
    const { data, error: apiError } = await useApi<FactureUI[]>(`http://127.0.0.1:8000/api/factures/?created_at=${today}`, { method: 'GET' });
    if (apiError.value) throw new Error(apiError.value);
    factures.value = Array.isArray(data.value)
      ? data.value.map(facture => {
          const total = Number(facture.total) ?? 0;
          const reste = facture.reste !== undefined ? Number(facture.reste) : 0;
          const verse = total - reste;
          return {
            ...facture,
            total,
            verse,
            reste,
            date: facture.created_at ? formatDate(facture.created_at) : 'Date inconnue'
          }
        })
      : [];
  } catch (err) {
    factures.value = [];
  } finally {
    loading.value = false;
  }
}

async function loadFacturesGlobal() {
  try {
    const { data, error: err } = await useApi<FactureUI[]>('http://127.0.0.1:8000/api/factures/', { method: 'GET' });
    if (err.value) throw new Error(err.value);
    allFactures.value = Array.isArray(data.value)
      ? data.value.map(facture => {
          const total = Number(facture.total) ?? 0;
          const reste = facture.reste !== undefined ? Number(facture.reste) : 0;
          const verse = total - reste;
          return {
            ...facture,
            total,
            verse,
            reste,
            date: facture.created_at ? formatDate(facture.created_at) : 'Date inconnue'
          }
        })
      : [];
  } catch (e) {
    allFactures.value = [];
  }
}

onMounted(() => {
  loadFacturesJour();
  loadFacturesGlobal();
});
</script>

<style scoped>
/* Dashboard style amélioré */
.kpi-card {
  background: linear-gradient(135deg, #e0e7ff 0%, #f0fdfa 100%);
  border-radius: 1.5rem;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07);
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: box-shadow 0.2s;
}
.kpi-card:hover {
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}
.kpi-title {
  font-size: 1.1rem;
  color: #2563eb;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.kpi-value {
  font-size: 2.2rem;
  font-weight: bold;
  color: #0f172a;
}
</style>

<template>
  <div class="p-6  min-h-screen">
    <!-- En-tête -->
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-xl md:text-3xl font-bold text-blue-400">Tableau de bord</h1>
      <div class="flex space-x-2">
        <select v-model="dateRange" class="px-3 py-2 border rounded-md text-sm">
          <option value="today">Aujourd'hui</option>
          <option value="week">Cette semaine</option>
          <option value="month">Ce mois</option>
          <option value="custom">Période personnalisée</option>
        </select>
        <div v-if="dateRange === 'custom'" class="flex space-x-2">
          <input type="date" v-model="startDate" class="px-3 py-2 border rounded-md text-sm">
          <input type="date" v-model="endDate" class="px-3 py-2 border rounded-md text-sm">
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
      <KpiCard class="kpi-card" title="Chiffre d'affaires encaissé" :value="formatCurrency(chiffreAffaireEncaisse)" icon="currency-euro" color="blue" />
      <KpiCard class="kpi-card" title="Bénéfice" :value="formatCurrency(margeTotale)" icon="trending-up" color="green" />
      <KpiCard class="kpi-card" title="Ordinateurs en Stock" :value="computerCount" icon="monitor" color="blue" />
      <KpiCard class="kpi-card" title="Téléphones en Stock" :value="phoneCount" icon="device-mobile" color="blue" />
      <KpiCard class="kpi-card" title="Accessoires" :value="accessoryCount" icon="shopping-bag" color="blue" />
      <KpiCard class="kpi-card" title="Dettes totales" :value="formatCurrency(totalDetteGlobale)" icon="credit-card" color="red" colSpan="lg:col-span-2" />
    </div>

    <!-- Liste des factures -->
    <div class="bg-white rounded-2xl shadow-md p-6 max-w-full overflow-x-auto">
      <h2 class="text-xl md:text-3xl font-bold text-blue-400">Factures du jour</h2>
      <div v-if="loading" class="text-center text-gray-500 animate-pulse">Chargement en cours...</div>
      <table v-else class="min-w-[800px] w-full text-sm text-left text-gray-700">
        <thead class="bg-gray-100 text-xs uppercase text-gray-600">
          <tr>
            <th class="px-4 py-3">Numéro</th>
            <th class="px-4 py-3">Date</th>
            <th class="px-4 py-3">Type</th>
            <th class="px-4 py-3">Nom</th>
            <th class="px-4 py-3">Total</th>
            <th class="px-4 py-3">Versé</th>
            <th class="px-4 py-3">Reste</th>
            <th class="px-4 py-3">Statut</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-for="facture in factures" :key="facture.id" class="hover:bg-gray-50 transition duration-150 ease-in-out">
            <td class="px-4 py-3 font-medium text-gray-800">{{ facture.numero }}</td>
            <td class="px-4 py-3">{{ facture.date }}</td>
            <td class="px-4 py-3 capitalize">{{ facture.type }}</td>
            <td class="px-4 py-3">{{ facture.nom }}</td>
            <td class="px-4 py-3">{{ formatCurrency(facture.total) }}</td>
            <td class="px-4 py-3">{{ formatCurrency(facture.verse) }}</td>
            <td class="px-4 py-3">{{ formatCurrency(facture.reste) }}</td>
            <td class="px-4 py-3">
              <span :class="[
                'inline-block px-3 py-1 text-xs font-semibold rounded-full',
                facture.status === 'payé' 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-yellow-100 text-yellow-700'
              ]">
                {{ facture.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
  
  