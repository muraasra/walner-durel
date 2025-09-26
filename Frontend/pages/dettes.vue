<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useFetch } from '#app'
import { useNotification } from '@/types/useNotification'
import { useAuthStore } from '@/stores/auth'

type DebtStatus = 'pending' | 'partially_paid' | 'paid'

interface DebtPayment {
  id: number
  amount: string | number
  created_at: string
}

interface DebtItem {
  id: number
  reference: string
  machine_description: string
  technician_name: string
  reason: string
  amount: string | number
  status: DebtStatus
  expected_return_date: string
  created_at: string
  total_paid: string | number
  amount_due: string | number
  payments: DebtPayment[]
}

interface PaginatedDebtResponse {
  count: number
  next: string | null
  previous: string | null
  results: DebtItem[]
}

const auth = useAuthStore()
const { success, error: notifyError } = useNotification()

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

const query = computed(() => ({
  page: filters.page,
  include_payments: true,
  ...(filters.status !== 'all' ? { status: filters.status } : {}),
  ...(filters.q ? { q: filters.q } : {}),
  ...(filters.from ? { from: filters.from } : {}),
  ...(filters.to ? { to: filters.to } : {}),
}))

const headers = computed(() => ({
  'Content-Type': 'application/json',
  ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
}))

const { data, pending, error, refresh } = await useFetch<PaginatedDebtResponse | DebtItem[]>('/api/debts/', {
  query,
  watch: [query],
  immediate: true,
  headers,
})

watch(error, (err) => {
  if (err?.value) {
    notifyError('Impossible de charger les dettes.')
  }
})

watch([() => filters.status, () => filters.q, () => filters.from, () => filters.to], () => {
  filters.page = 1
})

const debts = computed<DebtItem[]>(() => {
  if (!data.value) return []
  if (Array.isArray(data.value)) return data.value
  return data.value.results ?? []
})

const pagination = computed<PaginatedDebtResponse>(() => {
  if (!data.value || Array.isArray(data.value)) {
    return {
      count: debts.value.length,
      next: null,
      previous: null,
      results: debts.value,
    }
  }
  return data.value
})

const pageSize = computed(() => (debts.value.length > 0 ? debts.value.length : 10))
const totalPages = computed(() => {
  if (!pagination.value.count || pageSize.value === 0) return 1
  return Math.max(1, Math.ceil(pagination.value.count / pageSize.value))
})

const totalAmount = computed(() =>
  debts.value.reduce((sum, debt) => sum + Number(debt.amount ?? 0), 0)
)
const totalOutstanding = computed(() =>
  debts.value.reduce((sum, debt) => sum + Number(debt.amount_due ?? 0), 0)
)

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'XAF',
    maximumFractionDigits: 0,
  }).format(amount ?? 0)
}

const showCreateModal = ref(false)
const showPaymentModal = ref(false)
const isSubmitting = ref(false)
const isPaying = ref(false)
const selectedDebt = ref<DebtItem | null>(null)
const paymentAmount = ref('')
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
  debtForm.reference = debt.reference
  debtForm.machine_description = debt.machine_description
  debtForm.technician_name = debt.technician_name
  debtForm.reason = debt.reason
  debtForm.amount = String(debt.amount)
  debtForm.expected_return_date = debt.expected_return_date
  formErrors.value = {}
  showCreateModal.value = true
}

function openPaymentModal(debt: DebtItem) {
  selectedDebt.value = debt
  paymentAmount.value = ''
  isPaying.value = false
  showPaymentModal.value = true
}

async function submitDebt() {
  isSubmitting.value = true
  formErrors.value = {}
  try {
    const payload = {
      reference: debtForm.reference || undefined,
      machine_description: debtForm.machine_description,
      technician_name: debtForm.technician_name,
      reason: debtForm.reason,
      amount: Number(debtForm.amount),
      expected_return_date: debtForm.expected_return_date,
    }
    if (!payload.machine_description || !payload.technician_name || !payload.amount || !payload.expected_return_date) {
      notifyError('Merci de remplir tous les champs obligatoires.')
      isSubmitting.value = false
      return
    }

    const url = selectedDebt.value ? `/api/debts/${selectedDebt.value.id}/` : '/api/debts/'
    const method = selectedDebt.value ? 'PUT' : 'POST'

    await $fetch(url, {
      method,
      body: payload,
      headers: headers.value,
    })

    success(selectedDebt.value ? 'Dette mise à jour avec succès.' : 'Dette créée avec succès.')
    showCreateModal.value = false
    selectedDebt.value = null
    resetForm()
    await refresh()
  } catch (err: any) {
    if (err?.data) {
      formErrors.value = err.data
    }
    notifyError("Une erreur est survenue lors de l'enregistrement de la dette.")
  } finally {
    isSubmitting.value = false
  }
}

async function submitPayment() {
  if (!selectedDebt.value) return
  const amount = Number(paymentAmount.value)
  if (!amount || amount <= 0) {
    notifyError('Le montant saisi est invalide.')
    return
  }
  isPaying.value = true
  try {
    await $fetch(`/api/debts/${selectedDebt.value.id}/pay/`, {
      method: 'PATCH',
      body: { paid_amount: amount },
      headers: headers.value,
    })
    success('Paiement enregistré avec succès.')
    showPaymentModal.value = false
    selectedDebt.value = null
    paymentAmount.value = ''
    await refresh()
  } catch (err) {
    notifyError("Impossible d'enregistrer le paiement.")
  } finally {
    isPaying.value = false
  }
}

function statusBadgeClass(status: DebtStatus) {
  switch (status) {
    case 'paid':
      return 'bg-green-100 text-green-600'
    case 'partially_paid':
      return 'bg-orange-100 text-orange-600'
    default:
      return 'bg-red-100 text-red-600'
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
        <h1 class="text-2xl font-bold text-blue-500 md:text-3xl">Dettes de l'entreprise</h1>
        <p class="text-sm text-gray-500">Suivi des machines confiées aux techniciens et des paiements associés.</p>
      </div>
      <button
        type="button"
        class="inline-flex items-center rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white shadow hover:bg-blue-600"
        @click="openCreateModal"
      >
        Nouvelle dette
      </button>
    </div>

    <div class="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div class="flex flex-col">
          <label class="text-xs font-semibold text-gray-500">Recherche</label>
          <input
            v-model="filters.q"
            type="text"
            placeholder="Référence, technicien..."
            class="mt-1 rounded-lg border px-3 py-2 text-sm shadow-sm"
          />
        </div>
        <div class="flex flex-col">
          <label class="text-xs font-semibold text-gray-500">Statut</label>
          <select v-model="filters.status" class="mt-1 rounded-lg border px-3 py-2 text-sm shadow-sm">
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
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

    <div class="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-100">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
            <tr>
              <th class="px-4 py-3">Référence</th>
              <th class="px-4 py-3">Technicien</th>
              <th class="px-4 py-3">Machine</th>
              <th class="px-4 py-3">Motif</th>
              <th class="px-4 py-3 text-right">Montant</th>
              <th class="px-4 py-3 text-right">Restant dû</th>
              <th class="px-4 py-3">Statut</th>
              <th class="px-4 py-3">Retour prévu</th>
              <th class="px-4 py-3">Créée le</th>
              <th class="px-4 py-3 text-center">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 bg-white">
            <tr
              v-for="debt in debts"
              :key="debt.id"
              :class="['transition-colors', isOverdue(debt) ? 'bg-red-50/40' : 'hover:bg-slate-50']"
            >
              <td class="px-4 py-3 font-medium text-slate-700">{{ debt.reference }}</td>
              <td class="px-4 py-3 text-slate-700">{{ debt.technician_name }}</td>
              <td class="px-4 py-3 text-slate-600">{{ debt.machine_description }}</td>
              <td class="px-4 py-3 text-slate-500">{{ debt.reason || '—' }}</td>
              <td class="px-4 py-3 text-right font-semibold text-slate-700">
                {{ formatCurrency(Number(debt.amount)) }}
              </td>
              <td class="px-4 py-3 text-right font-semibold" :class="Number(debt.amount_due) > 0 ? 'text-orange-600' : 'text-green-600'">
                {{ formatCurrency(Number(debt.amount_due)) }}
              </td>
              <td class="px-4 py-3">
                <span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold" :class="statusBadgeClass(debt.status)">
                  {{ debt.status === 'pending' ? 'En attente' : debt.status === 'partially_paid' ? 'Partiellement payé' : 'Payé' }}
                </span>
              </td>
              <td class="px-4 py-3 text-slate-600">
                <span :class="isOverdue(debt) ? 'font-semibold text-red-600' : ''">
                  {{ formatDate(debt.expected_return_date) }}
                </span>
              </td>
              <td class="px-4 py-3 text-slate-500">{{ formatDate(debt.created_at) }}</td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-2">
                  <button
                    type="button"
                    class="rounded-lg border border-slate-200 px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
                    @click="openEditModal(debt)"
                  >
                    Éditer
                  </button>
                  <button
                    type="button"
                    class="rounded-lg bg-blue-500 px-3 py-1 text-xs font-medium text-white hover:bg-blue-600"
                    @click="openPaymentModal(debt)"
                  >
                    Paiement
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!debts.length">
              <td colspan="10" class="px-4 py-6 text-center text-sm text-gray-500">Aucune dette trouvée pour les filtres sélectionnés.</td>
            </tr>
          </tbody>
          <tfoot v-if="debts.length" class="bg-slate-50 text-sm font-semibold text-slate-700">
            <tr>
              <td colspan="4" class="px-4 py-3 text-right">Totaux</td>
              <td class="px-4 py-3 text-right">{{ formatCurrency(totalAmount) }}</td>
              <td class="px-4 py-3 text-right">{{ formatCurrency(totalOutstanding) }}</td>
              <td colspan="4"></td>
            </tr>
          </tfoot>
        </table>
      </div>
      <div class="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-sm text-gray-500">
        <span>Page {{ filters.page }} sur {{ totalPages }}</span>
        <div class="flex gap-2">
          <button
            type="button"
            class="rounded-lg border border-slate-200 px-3 py-1 text-xs font-medium hover:bg-slate-100"
            :disabled="filters.page === 1"
            @click="filters.page = Math.max(1, filters.page - 1)"
          >
            Précédent
          </button>
          <button
            type="button"
            class="rounded-lg border border-slate-200 px-3 py-1 text-xs font-medium hover:bg-slate-100"
            :disabled="filters.page >= totalPages"
            @click="filters.page = Math.min(totalPages, filters.page + 1)"
          >
            Suivant
          </button>
        </div>
      </div>
    </div>

    <transition name="fade">
      <div v-if="pending" class="fixed inset-0 z-20 flex items-center justify-center bg-white/40">
        <div class="flex items-center gap-3 rounded-xl bg-white px-6 py-4 shadow-lg ring-1 ring-slate-100">
          <span class="h-3 w-3 animate-ping rounded-full bg-blue-500"></span>
          <p class="text-sm text-slate-600">Chargement des données...</p>
        </div>
      </div>
    </transition>

    <UModal v-model="showCreateModal" :title="selectedDebt ? 'Modifier la dette' : 'Créer une dette'">
      <form class="space-y-4" @submit.prevent="submitDebt">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label class="text-xs font-semibold text-gray-500">Référence</label>
            <input v-model="debtForm.reference" type="text" class="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm" />
            <p v-if="formErrors.reference" class="mt-1 text-xs text-red-500">{{ formErrors.reference.join(', ') }}</p>
          </div>
          <div>
            <label class="text-xs font-semibold text-gray-500">Technicien *</label>
            <input v-model="debtForm.technician_name" type="text" class="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm" required />
            <p v-if="formErrors.technician_name" class="mt-1 text-xs text-red-500">{{ formErrors.technician_name.join(', ') }}</p>
          </div>
        </div>
        <div>
          <label class="text-xs font-semibold text-gray-500">Description de la machine *</label>
          <textarea
            v-model="debtForm.machine_description"
            rows="3"
            class="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm"
            required
          ></textarea>
          <p v-if="formErrors.machine_description" class="mt-1 text-xs text-red-500">{{ formErrors.machine_description.join(', ') }}</p>
        </div>
        <div>
          <label class="text-xs font-semibold text-gray-500">Motif</label>
          <input v-model="debtForm.reason" type="text" class="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm" />
        </div>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label class="text-xs font-semibold text-gray-500">Montant *</label>
            <input v-model="debtForm.amount" type="number" min="0" step="0.01" class="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm" required />
            <p v-if="formErrors.amount" class="mt-1 text-xs text-red-500">{{ formErrors.amount.join(', ') }}</p>
          </div>
          <div>
            <label class="text-xs font-semibold text-gray-500">Retour prévu *</label>
            <input v-model="debtForm.expected_return_date" type="date" class="mt-1 w-full rounded-lg border px-3 py-2 text-sm shadow-sm" required />
            <p v-if="formErrors.expected_return_date" class="mt-1 text-xs text-red-500">{{ formErrors.expected_return_date.join(', ') }}</p>
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium" @click="showCreateModal = false">
            Annuler
          </button>
          <button
            type="submit"
            class="rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
        </div>
      </form>
    </UModal>

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
          <button type="button" class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium" @click="showPaymentModal = false">
            Annuler
          </button>
          <button
            type="submit"
            class="rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600"
            :disabled="isPaying"
          >
            {{ isPaying ? 'Validation...' : 'Enregistrer le paiement' }}
          </button>
        </div>
      </form>
    </UModal>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
