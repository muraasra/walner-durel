<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from 'vue'
import { useNotification } from '@/types/useNotification'
import { useApi } from '@/stores/useApi'

const { public: { apiBase = 'http://127.0.0.1:8000/api' } } = useRuntimeConfig()
const { success, errors } = useNotification()

// --- Types
type DebtStatus = 'pending' | 'partially_paid' | 'paid'

interface DebtPayment {
  id: number
  amount: string | number
  created_at: string
}

interface DebtItem {
  id: number
  reference?: string
  machine_description: string
  technician_name: string
  reason?: string
  amount: string | number
  status: DebtStatus
  expected_return_date: string       // 'YYYY-MM-DD'
  created_at: string
  total_paid?: string | number
  amount_due?: string | number
  payments?: DebtPayment[]
}

interface PaginatedDebtResponse {
  count: number
  next: string | null
  previous: string | null
  results: DebtItem[]
}

// --- Filtres & pagination
const filters = reactive({
  status: 'all',
  q: '',
  from: '',
  to: '',
  page: 1,
})

const statusOptions: { label: string; value: string }[] = [
  { label: 'Tous les statuts', value: 'all' },
  { label: 'En attente', value: 'pending' },
  { label: 'Partiellement payé', value: 'partially_paid' },
  { label: 'Payé', value: 'paid' },
]

// --- State liste
const debts = ref<DebtItem[]>([])
const pagination = ref<PaginatedDebtResponse>({ count: 0, next: null, previous: null, results: [] })
const loading = ref(false)

// --- Fetch list
async function fetchDebts() {
  loading.value = true
  const { data, error } = await useApi<PaginatedDebtResponse | DebtItem[]>(`${apiBase}/debts/`, {
    method: 'GET',
    query: {
      page: filters.page,
      include_payments: true,
      ...(filters.status !== 'all' ? { status: filters.status } : {}),
      ...(filters.q ? { q: filters.q } : {}),
      ...(filters.from ? { from_date: filters.from } : {}), // mapping correct
      ...(filters.to ? { to_date: filters.to } : {}),       // mapping correct
    }
  })

  if (error.value) {
    errors("Impossible de charger les dettes.")
    debts.value = []
    pagination.value = { count: 0, next: null, previous: null, results: [] }
  } else if (Array.isArray(data.value)) {
    debts.value = data.value
    pagination.value = { count: data.value.length, next: null, previous: null, results: data.value }
  } else if (data.value) {
    debts.value = data.value.results ?? []
    pagination.value = data.value
  }
  loading.value = false
}

onMounted(fetchDebts)
watch([() => filters.status, () => filters.q, () => filters.from, () => filters.to], () => {
  filters.page = 1
  fetchDebts()
})
watch(() => filters.page, fetchDebts)

// --- Totaux
const totalAmount = computed(() => debts.value.reduce((s, d) => s + Number(d.amount ?? 0), 0))
const totalOutstanding = computed(() => debts.value.reduce((s, d) => s + Number(d.amount_due ?? 0), 0))

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF', maximumFractionDigits: 0 }).format(amount ?? 0)
}

// --- Create/Edit form
const showCreateModal = ref(false)
const isSubmitting = ref(false)
const selectedDebt = ref<DebtItem | null>(null)
const formErrors = ref<Record<string, string[]>>({})

const debtForm = reactive({
  reference: '',
  machine_description: '',
  technician_name: '',
  reason: '',
  amount: '',
  expected_return_date: '',
})

function resetForm() {
  debtForm.reference = ''
  debtForm.machine_description = ''
  debtForm.technician_name = ''
  debtForm.reason = ''
  debtForm.amount = ''
  debtForm.expected_return_date = ''
  formErrors.value = {}
}

function openCreateModal() {
  resetForm()
  selectedDebt.value = null
  showCreateModal.value = true
}

function openEditModal(debt: DebtItem) {
  selectedDebt.value = debt
  debtForm.reference = debt.reference || ''
  debtForm.machine_description = debt.machine_description
  debtForm.technician_name = debt.technician_name
  debtForm.reason = debt.reason || ''
  debtForm.amount = String(debt.amount)
  debtForm.expected_return_date = debt.expected_return_date
  formErrors.value = {}
  showCreateModal.value = true
}

async function submitDebt() {
  isSubmitting.value = true
  formErrors.value = {}

  try {
    const payload = {
      reference: debtForm.reference || undefined,
      machine_description: debtForm.machine_description,
      technician_name: debtForm.technician_name,
      reason: debtForm.reason || '',
      amount: Number(debtForm.amount),
      expected_return_date: debtForm.expected_return_date, // YYYY-MM-DD
    }

    if (!payload.machine_description || !payload.technician_name || !payload.amount || !payload.expected_return_date) {
      errors('Merci de remplir tous les champs obligatoires.')
      isSubmitting.value = false
      return
    }

    const url = selectedDebt.value
      ? `${apiBase}/debts/${selectedDebt.value.id}/`
      : `${apiBase}/debts/`
    const method = selectedDebt.value ? 'PUT' : 'POST'

    const { error } = await useApi(url, { method, body: payload })
    if (error.value) {
      formErrors.value = (error.value as any) ?? {}
      errors('Enregistrement échoué.')
      return
    }

    success(selectedDebt.value ? 'Dette mise à jour avec succès.' : 'Dette créée avec succès.')
    showCreateModal.value = false
    selectedDebt.value = null
    resetForm()
    await fetchDebts()
  } catch {
    errors("Une erreur est survenue lors de l'enregistrement de la dette.")
  } finally {
    isSubmitting.value = false
  }
}

// --- Paiement
const showPaymentModal = ref(false)
const isPaying = ref(false)
const paymentAmount = ref('')

function openPaymentModal(debt: DebtItem) {
  selectedDebt.value = debt
  paymentAmount.value = ''
  isPaying.value = false
  showPaymentModal.value = true
}

async function submitPayment() {
  if (!selectedDebt.value) return
  const amount = Number(paymentAmount.value)
  if (!amount || amount <= 0) {
    errors('Le montant saisi est invalide.')
    return
  }
  isPaying.value = true
  try {
    const { error } = await useApi(`${apiBase}/debts/${selectedDebt.value.id}/pay/`, {
      method: 'PATCH',
      body: { paid_amount: amount }
    })
    if (error.value) {
      errors("Impossible d'enregistrer le paiement.")
      return
    }
    success('Paiement enregistré avec succès.')
    showPaymentModal.value = false
    selectedDebt.value = null
    paymentAmount.value = ''
    await fetchDebts()
  } catch {
    errors("Impossible d'enregistrer le paiement.")
  } finally {
    isPaying.value = false
  }
}

// --- UI helpers
function statusBadgeClass(status: DebtStatus) {
  switch (status) {
    case 'paid': return 'bg-green-100 text-green-600'
    case 'partially_paid': return 'bg-orange-100 text-orange-600'
    default: return 'bg-red-100 text-red-600'
  }
}

function isOverdue(debt: DebtItem) {
  if (debt.status === 'paid') return false
  const today = new Date().toISOString().split('T')[0]
  return debt.expected_return_date < today
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('fr-FR')
}
</script>

<template>
  <div class="space-y-6 p-6">
    <div class="flex flex-col justify-between gap-4 md:flex-row md:items-center">
      <div>
        <h1 class="text-2xl font-bold text-blue-400 md:text-3xl">Dettes </h1>
        <p class="text-sm text-gray-500">Suivi des machines confiées aux techniciens et des paiements associés.</p>
      </div>
      <button
        type="button"
        class="inline-flex items-center rounded-lg bg-blue-400 px-4 py-2 text-sm font-medium text-white shadow hover:bg-blue-600"
        @click="openCreateModal"
      >
        Nouvelle dette
      </button>
    </div>

    <!-- Filtres -->
    <div class="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div class="flex flex-col">
          <label class="text-xs font-semibold text-gray-500">Recherche</label>
          <input v-model="filters.q" type="text" placeholder="Référence, technicien..." class="mt-1 rounded-lg border px-3 py-2 text-sm shadow-sm" />
        </div>
        <div class="flex flex-col">
          <label class="text-xs font-semibold text-gray-500">Statut</label>
          <select v-model="filters.status" class="mt-1 rounded-lg border px-3 py-2 text-sm shadow-sm">
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
        </div>
        <div class="flex flex-col">
          <label class="text-xs font-semibold text-gray-500">Du</label>
          <input v-model="filters.from" type="date" class="mt-1 rounded-lg border px-3 py-2 text-sm shadow-sm" />
        </div>
        <div class="flex flex-col">
          <label class="text-xs font-semibold text-gray-500">Au</label>
          <input v-model="filters.to" type="date" class="mt-1 rounded-lg border px-3 py-2 text-sm shadow-sm" />
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-hidden rounded-xl bg-white shadow ring-1 ring-gray-100">
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm border-separate border-spacing-0">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 font-semibold text-gray-700 text-base border-b border-gray-200">Référence</th>
              <th class="px-4 py-3 font-semibold text-gray-700 text-base border-b border-gray-200">Technicien</th>
              <th class="px-4 py-3 font-semibold text-gray-700 text-base border-b border-gray-200">Machine</th>
              <th class="px-4 py-3 font-semibold text-gray-700 text-base border-b border-gray-200">Motif</th>
              <th class="px-4 py-3 font-semibold text-gray-700 text-base border-b border-gray-200 text-right">Montant</th>
              <th class="px-4 py-3 font-semibold text-gray-700 text-base border-b border-gray-200 text-right">Restant dû</th>
              <th class="px-4 py-3 font-semibold text-gray-700 text-base border-b border-gray-200">Statut</th>
              <th class="px-4 py-3 font-semibold text-gray-700 text-base border-b border-gray-200">Retour prévu</th>
              <th class="px-4 py-3 font-semibold text-gray-700 text-base border-b border-gray-200">Créée le</th>
              <th class="px-4 py-3 font-semibold text-gray-700 text-base border-b border-gray-200 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="debt in debts" :key="debt.id" :class="[isOverdue(debt) ? 'bg-red-50/40' : 'bg-white', 'hover:bg-gray-50 transition']">
              <td class="px-4 py-3 font-medium text-gray-800 border-b border-gray-100">{{ debt.reference || '—' }}</td>
              <td class="px-4 py-3 text-gray-800 border-b border-gray-100">{{ debt.technician_name }}</td>
              <td class="px-4 py-3 text-gray-700 border-b border-gray-100">{{ debt.machine_description }}</td>
              <td class="px-4 py-3 text-gray-600 border-b border-gray-100">{{ debt.reason || '—' }}</td>
              <td class="px-4 py-3 text-right font-semibold text-gray-900 border-b border-gray-100">{{ formatCurrency(Number(debt.amount)) }}</td>
              <td class="px-4 py-3 text-right font-semibold border-b border-gray-100" :class="Number(debt.amount_due) > 0 ? 'text-orange-600' : 'text-green-600'">
                {{ formatCurrency(Number(debt.amount_due)) }}
              </td>
              <td class="px-4 py-3 border-b border-gray-100">
                <span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold" :class="statusBadgeClass(debt.status)">
                  {{ debt.status === 'pending' ? 'En attente' : debt.status === 'partially_paid' ? 'Partiellement payé' : 'Payé' }}
                </span>
              </td>
              <td class="px-4 py-3 text-gray-700 border-b border-gray-100">
                <span :class="isOverdue(debt) ? 'font-semibold text-red-600' : ''">{{ formatDate(debt.expected_return_date) }}</span>
              </td>
              <td class="px-4 py-3 text-gray-500 border-b border-gray-100">{{ formatDate(debt.created_at) }}</td>
              <td class="px-4 py-3 text-center border-b border-gray-100">
                <div class="flex items-center justify-center gap-2">
                  <UButton variant="outline" color="blue" size="sm" @click="openEditModal(debt)">Éditer</UButton>
                  <UButton variant="outline" color="green" size="sm" @click="openPaymentModal(debt)">Paiement</UButton>
                </div>
              </td>
            </tr>
            <tr v-if="!debts.length && !loading">
              <td colspan="10" class="px-4 py-6 text-center text-sm text-gray-500">Aucune dette trouvée pour les filtres sélectionnés.</td>
            </tr>
          </tbody>

          <tfoot v-if="debts.length">
            <tr class="bg-gray-50">
              <td colspan="4"></td>
              <td class="px-4 py-4 text-center text-lg font-bold text-blue-400">{{ formatCurrency(totalAmount) }}</td>
              <td class="px-4 py-4 text-center text-lg font-bold text-orange-600">{{ formatCurrency(totalOutstanding) }}</td>
              <td colspan="4"></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Pagination -->
      <div class="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-sm text-gray-500">
        <span>Page {{ filters.page }} sur {{ Math.max(1, Math.ceil((pagination.count || 0) / (debts.length || 1))) }}</span>
        <div class="flex gap-2">
          <button type="button" class="rounded-lg border border-slate-200 px-3 py-1 text-xs font-medium hover:bg-slate-100" :disabled="filters.page === 1" @click="filters.page = Math.max(1, filters.page - 1)">
            Précédent
          </button>
          <button type="button" class="rounded-lg border border-slate-200 px-3 py-1 text-xs font-medium hover:bg-slate-100" :disabled="filters.page >= Math.max(1, Math.ceil((pagination.count || 0) / (debts.length || 1)))" @click="filters.page = Math.min(Math.max(1, Math.ceil((pagination.count || 0) / (debts.length || 1))), filters.page + 1)">
            Suivant
          </button>
        </div>
      </div>
    </div>

    <!-- Overlay loading -->
    <transition name="fade">
      <div v-if="loading" class="fixed inset-0 z-20 flex items-center justify-center bg-white/40">
        <div class="flex items-center gap-3 rounded-xl bg-white px-6 py-4 shadow-lg ring-1 ring-slate-100">
          <span class="h-3 w-3 animate-ping rounded-full bg-blue-400"></span>
          <p class="text-sm text-slate-600">Chargement des données...</p>
        </div>
      </div>
    </transition>

    <!-- Modal création / édition -->
    <UModal v-model="showCreateModal">
      <div class="p-4 space-y-4">
        <h3 class="text-lg font-semibold">{{ selectedDebt ? 'Modifier la dette' : 'Créer une dette' }}</h3>
        <UForm :state="debtForm" @submit="submitDebt" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <UFormGroup label="Référence" name="reference">
            <UInput v-model.trim="debtForm.reference" placeholder="Réf. interne ou client" color="blue" />
            <p v-if="formErrors.reference" class="mt-1 text-xs text-red-500">{{ formErrors.reference.join(', ') }}</p>
          </UFormGroup>

          <UFormGroup label="Technicien *" name="technician_name">
            <UInput v-model.trim="debtForm.technician_name" placeholder="Nom du technicien" color="blue" required />
            <p v-if="formErrors.technician_name" class="mt-1 text-xs text-red-500">{{ formErrors.technician_name.join(', ') }}</p>
          </UFormGroup>

          <UFormGroup label="Description" name="machine_description" class="md:col-span-2">
            <UTextarea v-model.trim="debtForm.machine_description" :rows="3" placeholder="Détails machine, modèle, emprunt, etc." color="blue" required />
            <p v-if="formErrors.machine_description" class="mt-1 text-xs text-red-500">{{ formErrors.machine_description.join(', ') }}</p>
          </UFormGroup>

          <UFormGroup label="Motif" name="reason" class="md:col-span-2">
            <UInput v-model.trim="debtForm.reason" placeholder="Motif de la dette (optionnel)" color="blue" />
          </UFormGroup>

          <UFormGroup label="Montant *" name="amount">
            <UInput type="number" v-model.number="debtForm.amount" min="0" step="0.01" color="blue" required />
            <p v-if="formErrors.amount" class="mt-1 text-xs text-red-500">{{ formErrors.amount.join(', ') }}</p>
          </UFormGroup>

          <UFormGroup label="Retour prévu *" name="expected_return_date">
            <UInput type="date" v-model="debtForm.expected_return_date" color="blue" required />
            <p v-if="formErrors.expected_return_date" class="mt-1 text-xs text-red-500">{{ formErrors.expected_return_date.join(', ') }}</p>
          </UFormGroup>

          <div class="md:col-span-2 flex justify-end gap-3 pt-2">
            <UButton type="button" color="gray" @click="showCreateModal = false">Annuler</UButton>
            <UButton type="submit" color="blue" :disabled="isSubmitting">
              {{ isSubmitting ? 'Enregistrement...' : 'Enregistrer' }}
            </UButton>
          </div>
        </UForm>
      </div>
    </UModal>

    <!-- Modal paiement -->
    <UModal v-model="showPaymentModal" title="Enregistrer un paiement">
      <form class="space-y-4" @submit.prevent="submitPayment">
        <p v-if="selectedDebt" class="text-sm text-slate-600">
          Montant restant dû :
          <span class="font-semibold text-blue-500">{{ formatCurrency(Number(selectedDebt.amount_due)) }}</span>
        </p>
        <div>
          <label class="text-xs font-semibold text-gray-500">Montant payé *</label>
          <input v-model="paymentAmount" type="number" min="0" step="0.01" class="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm" required />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium" @click="showPaymentModal = false">Annuler</button>
          <button type="submit" class="rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600" :disabled="isPaying">
            {{ isPaying ? 'Validation...' : 'Enregistrer le paiement' }}
          </button>
        </div>
      </form>
    </UModal>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>
