<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue';
  import KpiCard from '@/components/KpiCard.vue';
  import { useNotification } from '../types/useNotification';
  import { useApi } from '../stores/useApi';
  
  // États réactifs
  const dateRange = ref('today')
  const startDate = ref('')
  const endDate = ref('')
  const products = ref<Product[]>([])
  const debts = ref<Debt[]>([])
  
  // ! Produit
  interface Product {
    id: number
    reference: string,
    nomProduit: string,
    category:string,
    prix:number,
    description: string,
    quantiteTotale: number,
    statut: boolean,
    boutique: 1
  }

  const { data: produits } = await useApi<Product[]>('http://127.0.0.1:8000/api/produits/', {
    method: 'GET'
  });

  // * Computed qui compte les produits dont categorie === 'Ordinateur'
  const computerCount = computed(() => {
    if (!produits.value) return 0;
    return produits.value.filter(p => p.category.toLowerCase() === 'ordinateur').length;
  });

  const phoneCount = computed(() => {
    if (!produits.value) return 0;
    return produits.value.filter(p => p.category.toLowerCase() === 'telephone').length;
  });
  
  interface Debt {
    id: number
    partner: string
    amount: number
    dueDate: string
  }
  
  // Données calculées
  // const totalRevenue = computed(() => {
  //   // Calcul du chiffre d'affaires selon la période sélectionnée
  //   return products.value.reduce((sum, product) => {
  //     // À adapter selon votre logique métier
  //     return sum + (product.salePrice * product.quantity)
  //   }, 0)
  // })
  
  // const totalProfit = computed(() => {
  //   return products.value.reduce((sum, product) => {
  //     return sum + ((product.salePrice - product.purchasePrice) * product.quantity)
  //   }, 0)
  // })
  
  // const totalComputers = computed(() => {
  //   return products.value.filter(p => p.category === 'ordinateur').length
  // })
  
  // const totalPhones = computed(() => {
  //   return products.value.filter(p => p.category === 'telephone').length

  // })
  
  // const totalAccessories = computed(() => {
  //   return products.value.filter(p => p.category === 'accessoire').length
  // })
  
  // const totalDebt = computed(() => {
  //   return debts.value.reduce((sum, debt) => sum + debt.amount, 0)
  // })
  
  
  // Méthodes
  function formatCurrency(value: number): string {
    return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF' }).format(value)
  }
  
  function formatDate(dateString: string): string {
    const date = new Date(dateString)
    return date.toLocaleDateString('fr-FR')
  }
  
  // Chargement initial des données
  async function loadData() {

    
    debts.value = [
      { id: 1, partner: 'Partenaire X', amount: 5000, dueDate: '2023-10-15' },
    ]
  }
  
  onMounted(loadData)


//  !  Factures du jour 

interface FactureApi {
  id: number;
  type: string;
  nom: string;
  numero: string;
  total?: number; 
  verse?: number;
  status: string;
  created_at: string;
  created_by: number;
  boutique: number;
}

// Interface pour les données traitées
interface FactureUI {
  id: number;
  type: string;
  nom: string;
  numero: string;
  total: number;
  verse: number;
  reste: number; // Calculé dynamiquement
  status: string;
  date: string;
}

const factures = ref<FactureUI[]>([]);
const loading = ref(true);
const { success, error } = useNotification();
const  allFactures = ref<FactureUI[]>([]);

// calcul dette totale
const totalDetteGlobale = computed(() => {
  return allFactures.value.reduce((sum, f) => sum + ((f.total ?? 0) - (f.verse ?? 0)), 0)
});

// Chargement des factures du jour
async function loadFacturesJour() {
  try {
    loading.value = true;
    const today = new Date().toISOString().split('T')[0];
    // const today = '2025-05-11';
    console.log(`Fetching factures for date: ${today}`);
    
    const { data, error: apiError } = await useApi<FactureApi[]>(`http://127.0.0.1:8000/api/factures/?created_at=${today}`, {
      method: 'GET'
    });

    if (apiError.value) {
      console.error('API Error:', apiError.value);
      error("Erreur lors du chargement des factures");
      return;
    }

    if (!data.value || data.value.length === 0) {
      factures.value = [];
      error('Aucune facture trouvée pour aujourd\'hui');
      return;
    }

    // Mappez les données 
    factures.value = data.value.map(facture => ({
      id: facture.id,
      type: facture.type,
      nom: facture.nom,
      numero: facture.numero,
      total: facture.total ?? 0,
      verse: facture.verse ?? 0,
      reste: (facture.total ?? 0) - (facture.verse ?? 0),
      status: facture.status,
      date: facture.created_at ? new Date(facture.created_at).toLocaleDateString() : 'Date inconnue'
    }));

    success('Factures chargées avec succès');

  } catch (err) {
    console.error('Erreur lors de la récupération des factures:', err);
    error("Une erreur est survenue lors du chargement des factures");
    factures.value = [];
  } finally {
    loading.value = false;
  }
}

// Chargement des factures globales 

async function loadFacturesGlobal() {
  try {
    const { data, error: err } = await useApi<FactureApi[]>(`http://127.0.0.1:8000/api/factures/`, {
      method: 'GET'
    });

    if (err.value) {
      error('Erreur lors du chargement global');
      return;
    }

    allFactures.value = (data.value || []).map(facture => ({
      id: facture.id,
      type: facture.type,
      nom: facture.nom,
      numero: facture.numero,
      total: facture.total ?? 0,
      verse: facture.verse ?? 0,
      reste: (facture.total ?? 0) - (facture.verse ?? 0),
      status: facture.status,
      date: facture.created_at
        ? new Date(facture.created_at).toLocaleDateString()
        : 'Date inconnue'
    }));
  } catch (e) {
    console.error(e);
    error("Erreur serveur");
  }
}

// Appeler la fonction de chargement des factures au montage du composant
onMounted(() => {
  loadFacturesJour();
  loadFacturesGlobal();
});

  </script>
  
  <style scoped>
  /* Vous pouvez ajouter des styles supplémentaires ici si nécessaire */
  </style>

<template>
    <div class="p-6 bg-gray-50 min-h-screen">
      <!-- En-tête -->
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-2xl font-bold text-blue-400">Tableau de bord</h1>
        <div class="flex space-x-2">
          <select v-model="dateRange" class="px-3 py-2 border rounded-md text-sm">
            <option value="today">Aujourd'hui</option>
            <option value="week">Cette semaine</option>
            <option value="month">Ce mois</option>
            <option value="custom">Période personnalisée</option>
          </select>
          
          <!-- Date picker personnalisé si besoin -->
          <div v-if="dateRange === 'custom'" class="flex space-x-2">
            <input type="date" v-model="startDate" class="px-3 py-2 border rounded-md text-sm">
            <input type="date" v-model="endDate" class="px-3 py-2 border rounded-md text-sm">
          </div>
        </div>
      </div>
  
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <!-- <KpiCard 
          title="Chiffre d'affaires" 
          :value="formatCurrency(totalRevenue)" 
          icon="currency-euro"
          color="blue"
        />
        <KpiCard 
          title="Bénéfice" 
          :value="formatCurrency(totalProfit)" 
          icon="trending-up"
          color="green"
        /> -->
        <KpiCard 
          title="Ordinateurs en Stock" 
          :value="computerCount" 
          icon="monitor"
          color="blue"
        />
         <KpiCard 
          title="Téléphones en Stock" 
          :value="phoneCount" 
          icon="device-mobile"
          color="blue"
        />
        <!--
        <KpiCard 
          title="Accessoires" 
          :value="totalAccessories" 
          icon="shopping-bag"
          color="blue"
        /> -->
        <KpiCard 
          title="Dettes totales" 
          :value="formatCurrency(totalDetteGlobale )" 
          icon="credit-card"
          color="red"
          colSpan="lg:col-span-2"
        /> 
      </div>
  
      <!-- Liste des factures -->
<div class="bg-white rounded-2xl shadow-md p-6 max-w-full overflow-x-auto">
  <h2 class="text-2xl font-bold mb-6 text-blue-600">Factures du jour</h2>

  <div v-if="loading" class="text-center text-gray-500 animate-pulse">Chargement en cours...</div>

  <!-- Table -->
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
      <tr 
        v-for="facture in factures" 
        :key="facture.id"
        class="hover:bg-gray-50 transition duration-150 ease-in-out"
      >
        <td class="px-4 py-3 font-medium text-gray-800">{{ facture.numero }}</td>
        <td class="px-4 py-3">{{ facture.date }}</td>
        <td class="px-4 py-3 capitalize">{{ facture.type }}</td>
        <td class="px-4 py-3">{{ facture.nom }}</td>
        <td class="px-4 py-3">{{ formatCurrency(facture.total) }}</td>
        <td class="px-4 py-3">{{ formatCurrency(facture.verse) }}</td>
        <td class="px-4 py-3">{{ formatCurrency(facture.reste) }}</td>
        <td class="px-4 py-3">
          <span 
            :class="[
              'inline-block px-3 py-1 text-xs font-semibold rounded-full',
              facture.status === 'payé' 
                ? 'bg-green-100 text-green-700' 
                : 'bg-yellow-100 text-yellow-700'
            ]"
          >
            {{ facture.status }}
          </span>
        </td>
      </tr>
    </tbody>
  </table>
</div>
    </div>
  </template>
  
  