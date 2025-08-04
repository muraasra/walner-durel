<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useNotification } from '~/types/useNotification';

const auth = useAuthStore();
const { error } = useNotification();

interface JournalEntry {
  id: number;
  utilisateur: number;
  utilisateur_nom: string;
  boutique: number;
  boutique_nom: string;
  type_operation: string;
  description: string;
  details: any;
  date_operation: string;
  ip_address: string;
}

const journalEntries = ref<JournalEntry[]>([]);
const loading = ref(false);
const totalItems = ref(0);
const currentPage = ref(1);
const itemsPerPage = ref(10);

// Filtres
const selectedBoutique = ref('');
const selectedTypeOperation = ref('');
const selectedUtilisateur = ref('');
const dateDebut = ref('');
const dateFin = ref('');

const boutiques = ref([]);
const utilisateurs = ref([]);
const typesOperation = [
  { value: 'creation', label: 'Création' },
  { value: 'modification', label: 'Modification' },
  { value: 'suppression', label: 'Suppression' },
  { value: 'connexion', label: 'Connexion' },
  { value: 'deconnexion', label: 'Déconnexion' },
  { value: 'vente', label: 'Vente' },
  { value: 'achat', label: 'Achat' },
  { value: 'retour', label: 'Retour' },
];

function getTypeOperationColor(type: string): string {
  const colors = {
    creation: 'green',
    modification: 'blue',
    suppression: 'red',
    connexion: 'purple',
    deconnexion: 'gray',
    vente: 'green',
    achat: 'blue',
    retour: 'orange',
  };
  return colors[type] || 'gray';
}

const fetchJournal = async () => {
  try {
    loading.value = true;
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: itemsPerPage.value.toString(),
    });

    if (selectedBoutique.value) params.append('boutique', selectedBoutique.value);
    if (selectedTypeOperation.value) params.append('type_operation', selectedTypeOperation.value);
    if (selectedUtilisateur.value) params.append('utilisateur', selectedUtilisateur.value);
    if (dateDebut.value) params.append('date_debut', dateDebut.value);
    if (dateFin.value) params.append('date_fin', dateFin.value);

    const response = await fetch(`${auth.baseUrl}/api/journaux/?${params.toString()}`, {
      headers: {
        Authorization: `Bearer ${auth.token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors de la récupération du journal');
    }

    const data = await response.json();
    journalEntries.value = data.results || [];
    totalItems.value = data.count || 0;
  } catch (err) {
    console.error('Erreur:', err);
    error('Erreur lors de la récupération du journal');
  } finally {
    loading.value = false;
  }
};

const fetchBoutiques = async () => {
  try {
    const response = await fetch(`${auth.baseUrl}/api/boutiques/`, {
      headers: {
        Authorization: `Bearer ${auth.token}`,
      },
    });
    if (!response.ok) throw new Error('Erreur lors de la récupération des boutiques');
    const data = await response.json();
    boutiques.value = data.results || data;
  } catch (err) {
    console.error('Erreur:', err);
    error('Erreur lors de la récupération des boutiques');
  }
};

const fetchUtilisateurs = async () => {
  try {
    const response = await fetch(`${auth.baseUrl}/api/users/`, {
      headers: {
        Authorization: `Bearer ${auth.token}`,
      },
    });
    if (!response.ok) throw new Error('Erreur lors de la récupération des utilisateurs');
    const data = await response.json();
    utilisateurs.value = data.results || data;
  } catch (err) {
    console.error('Erreur:', err);
    error('Erreur lors de la récupération des utilisateurs');
  }
};

const resetFilters = () => {
  selectedBoutique.value = '';
  selectedTypeOperation.value = '';
  selectedUtilisateur.value = '';
  dateDebut.value = '';
  dateFin.value = '';
  currentPage.value = 1;
  fetchJournal();
};

onMounted(() => {
  fetchJournal();
  fetchBoutiques();
  fetchUtilisateurs();
});

watch([currentPage, itemsPerPage], () => {
  fetchJournal();
});

watch([selectedBoutique, selectedTypeOperation, selectedUtilisateur, dateDebut, dateFin], () => {
  currentPage.value = 1;
  fetchJournal();
});
</script>

<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-6">Journal des opérations</h1>

    <!-- Filtres -->
    <div class="bg-white p-4 rounded-lg shadow mb-6">
      <h2 class="text-lg font-semibold mb-4">Filtres</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <UFormGroup label="Boutique">
          <USelect
            v-model="selectedBoutique"
            :options="boutiques.map(b => ({ value: b.id, label: b.nom }))"
            placeholder="Sélectionner une boutique"
          />
        </UFormGroup>

        <UFormGroup label="Type d'opération">
          <USelect
            v-model="selectedTypeOperation"
            :options="typesOperation"
            placeholder="Sélectionner un type"
          />
        </UFormGroup>

        <UFormGroup label="Utilisateur">
          <USelect
            v-model="selectedUtilisateur"
            :options="utilisateurs.map(u => ({ value: u.id, label: `${u.first_name} ${u.last_name}` }))"
            placeholder="Sélectionner un utilisateur"
          />
        </UFormGroup>

        <UFormGroup label="Date début">
          <UInput type="date" v-model="dateDebut" />
        </UFormGroup>

        <UFormGroup label="Date fin">
          <UInput type="date" v-model="dateFin" />
        </UFormGroup>

        <div class="flex items-end">
          <UButton color="gray" @click="resetFilters">Réinitialiser</UButton>
        </div>
      </div>
    </div>

    <!-- Tableau des opérations -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <UTable
        :rows="journalEntries"
        :columns="[
          { key: 'date_operation', label: 'Date' },
          { key: 'utilisateur_nom', label: 'Utilisateur' },
          { key: 'boutique_nom', label: 'Boutique' },
          { key: 'type_operation', label: 'Type' },
          { key: 'description', label: 'Description' },
          { key: 'ip_address', label: 'IP' },
        ]"
        :loading="loading"
      >
        <template #date_operation-data="{ row }">
          {{ new Date(row.date_operation).toLocaleString() }}
        </template>
        <template #type_operation-data="{ row }">
          <UBadge :color="getTypeOperationColor(row.type_operation)">
            {{ row.type_operation }}
          </UBadge>
        </template>
      </UTable>

      <!-- Pagination -->
      <div class="p-4 flex justify-between items-center">
        <UPagination
          v-model="currentPage"
          :total="totalItems"
          :page-count="Math.ceil(totalItems / itemsPerPage)"
        />
        <USelect
          v-model="itemsPerPage"
          :options="[
            { value: 10, label: '10 par page' },
            { value: 25, label: '25 par page' },
            { value: 50, label: '50 par page' },
          ]"
        />
      </div>
    </div>
  </div>
</template> 