<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotification } from '~/types/useNotification'
import { useApi } from '@/stores/useApi'

// ✅ Récupère la base API (fallback local si non configuré)
const { public: { apiBase: cfgBase } } = useRuntimeConfig()
const API_BASE = (cfgBase && String(cfgBase).replace(/\/+$/,'')) || 'http://127.0.0.1:8000/api'

const auth = useAuthStore()
const { errors } = useNotification()

interface JournalEntry {
  id: number
  utilisateur: number
  utilisateur_nom: string
  boutique: number
  boutique_nom: string
  type_operation: string
  description: string
  details: any
  date_operation: string
  ip_address: string
}

interface JournalApiResponse {
  results: JournalEntry[]
  count: number
  [key: string]: any
}

type Boutique = { id: number; nom?: string; name?: string }
type UserApi = {
  id: number
  username?: string
  email?: string
  nom?: string; prenom?: string
  first_name?: string; last_name?: string
}

const journalEntries = ref<JournalEntry[]>([])
const loading = ref(false)
const totalItems = ref(0)
const currentPage = ref(1)
const itemsPerPage = ref(10)

// Filtres
const selectedBoutique = ref<string | number>('')
const selectedTypeOperation = ref('')
const selectedUtilisateur = ref<string | number>('')
const dateDebut = ref('')
const dateFin = ref('')

const boutiques = ref<Boutique[]>([])
const utilisateurs = ref<UserApi[]>([])

const typesOperation = [
  { value: 'creation', label: 'Création' },
  { value: 'modification', label: 'Modification' },
  { value: 'suppression', label: 'Suppression' },
  { value: 'connexion', label: 'Connexion' },
  { value: 'deconnexion', label: 'Déconnexion' },
  { value: 'vente', label: 'Vente' },
  { value: 'achat', label: 'Achat' },
  { value: 'retour', label: 'Retour' },
]

function getTypeOperationColor(type: string): 'primary' | 'success' | 'warning' | 'errors' | 'info' | 'default' | undefined {
  const colors: Record<string, 'primary' | 'success' | 'warning' | 'errors' | 'info' | 'default'> = {
    creation: 'success',
    modification: 'info',
    suppression: 'errors',
    connexion: 'primary',
    deconnexion: 'default',
    vente: 'success',
    achat: 'info',
    retour: 'warning',
  }
  return colors[type] || 'default'
}

// Options pour les selects (visuel inchangé)
const boutiqueOptions = computed(() =>
  boutiques.value.map(b => ({
    value: b.id,
    label: b.nom ?? b.name ?? `#${b.id}`,
  }))
)

const userOptions = computed(() =>
  utilisateurs.value.map(u => {
    const first = u.prenom ?? u.first_name ?? ''
    const last  = u.nom ?? u.last_name ?? ''
    const label = (first || last) ? `${first} ${last}`.trim() : (u.username ?? `#${u.id}`)
    return { value: u.id, label }
  })
)

const fetchJournal = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: itemsPerPage.value,
      _ts: Date.now(),
    }
    if (selectedBoutique.value) params.boutique = selectedBoutique.value
    if (selectedTypeOperation.value) params.type_operation = selectedTypeOperation.value
    if (selectedUtilisateur.value) params.utilisateur = selectedUtilisateur.value
    if (dateDebut.value) params.date_debut = dateDebut.value
    if (dateFin.value) params.date_fin = dateFin.value

    const query = Object.entries(params)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
      .join('&')

    const { data, error: apiError } = await useApi(`${API_BASE}/journaux/?${query}`, {
      method: 'GET',
      server: false,
    })
    if (apiError.value) throw new Error((apiError.value as any)?.detail || 'Erreur API journal')

    const res = data.value as any
    journalEntries.value = Array.isArray(res) ? res : (res?.results ?? [])
    totalItems.value     = Array.isArray(res) ? res.length : (res?.count ?? 0)
  } catch (err) {
    console.error('Erreur:', err)
    errors('Erreur lors de la récupération du journal')
  } finally {
    loading.value = false
  }
}

const fetchBoutiques = async () => {
  try {
    const { data, error: apiError } = await useApi(`${API_BASE}/boutiques/`, { method: 'GET', server: false })
    if (apiError.value) throw new Error('Erreur API boutiques')
    const v = data.value as any
    boutiques.value = Array.isArray(v) ? v : (v?.results ?? [])
  } catch (err) {
    console.error('Erreur:', err)
    errors('Erreur lors de la récupération des boutiques')
  }
}

const fetchUtilisateurs = async () => {
  try {
    // essai 1
    let { data, error: apiError } = await useApi(`${API_BASE}/users/`, { method: 'GET', server: false })
    // fallback
    if (apiError.value) {
      ;({ data, error: apiError } = await useApi(`${API_BASE}/utilisateurs/`, { method: 'GET', server: false }))
    }
    if (apiError.value) throw new Error('Erreur API utilisateurs')
    const v = data.value as any
    utilisateurs.value = Array.isArray(v) ? v : (v?.results ?? [])
  } catch (err) {
    console.error('Erreur:', err)
    errors('Erreur lors de la récupération des utilisateurs')
  }
}

const resetFilters = () => {
  selectedBoutique.value = ''
  selectedTypeOperation.value = ''
  selectedUtilisateur.value = ''
  dateDebut.value = ''
  dateFin.value = ''
  currentPage.value = 1
  fetchJournal()
}

onMounted(() => {
  fetchBoutiques()
  fetchUtilisateurs()
  fetchJournal()
})

watch([currentPage, itemsPerPage], fetchJournal)
watch([selectedBoutique, selectedTypeOperation, selectedUtilisateur, dateDebut, dateFin], () => {
  currentPage.value = 1
  fetchJournal()
})
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
            :options="boutiqueOptions"
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
            :options="userOptions"
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
          <UBadge :colors="getTypeOperationColor(row.type_operation)">
            {{ row.type_operation }}
          </UBadge>
        </template>
      </UTable>

      <!-- Pagination -->
      <div class="p-4 flex justify-between items-center">
        <UPagination
          v-model="currentPage"
          :total="totalItems"
          :page-size="itemsPerPage"
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
