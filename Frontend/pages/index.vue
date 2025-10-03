<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler,
} from 'chart.js'
import KpiCard from '@/components/KpiCard.vue'
import { useNotification } from '@/types/useNotification'
import { useAuthStore } from '@/stores/auth'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

type Period = 'month' | 'quarter' | 'year'
interface MetricsTimeseriesEntry { date: string; sales: number; debts: number; ca_global: number }
interface MetricsTechnician { technician_name: string; montant: number }
interface MetricsResponse {
  period: Period; sales_encaissees: number; dettes_en_cours: number; ca_global: number;
  top_techniciens: MetricsTechnician[]; timeseries: MetricsTimeseriesEntry[]
}

const { public: { apiBase = 'http://127.0.0.1:8000/api' } } = useRuntimeConfig()
const auth = useAuthStore()
const { addToast } = useNotification()
const notifyError = (m: string) => addToast(m, 'error')

const periodOptions = [
  { label: 'Ce mois', value: 'month' },
  { label: 'Ce trimestre', value: 'quarter' },
  { label: 'Cette année', value: 'year' },
] as const

const selectedPeriod = ref<Period>('month')
const lastUpdated = ref<Date | null>(null)
const pending = ref(false)
const metrics = ref<MetricsResponse | null>(null)

function fmt(d: Date) {
  return d.toISOString().slice(0, 10) // YYYY-MM-DD
}
function addMonths(d: Date, m: number) {
  const x = new Date(d)
  x.setMonth(x.getMonth() + m)
  return x
}
function getRangeFor(period: 'month' | 'quarter' | 'year') {
  const today = new Date()
  let from: Date
  if (period === 'month') {
    from = new Date(today.getFullYear(), today.getMonth(), 1)
  } else if (period === 'quarter') {
    // ✅ 3 derniers mois glissants (rolling)
    from = addMonths(today, -3)
  } else {
    from = new Date(today.getFullYear(), 0, 1)
  }
  return { from: fmt(from), to: fmt(today) }
}

async function loadMetrics() {
  try {
    pending.value = true
    const { from, to } = getRangeFor(selectedPeriod.value)
    const res = await $fetch<MetricsResponse>(`${apiBase}/metrics/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
      },
      query: {
        // on garde period pour compat, mais on pilote par from/to
        period: selectedPeriod.value,
        from, to,
        includeDebts: true,
        include_debts: true,
        _ts: Date.now(),
      },
      cache: 'no-cache',
    })
    metrics.value = res
    lastUpdated.value = new Date()
  } catch (e) {
    notifyError('Impossible de charger les indicateurs du tableau de bord.')
  } finally {
    pending.value = false
  }
}


watch(selectedPeriod, () => loadMetrics(), { immediate: true })

const isInitialLoading = computed(() => pending.value && !metrics.value)
const caGlobal = computed(() => metrics.value?.ca_global ?? 0)
const ventesEncaissees = computed(() => metrics.value?.sales_encaissees ?? 0)
const dettesEnCours = computed(() => metrics.value?.dettes_en_cours ?? 0)
const topTechnicians = computed(() => metrics.value?.top_techniciens ?? [])
const timeseries = computed(() => metrics.value?.timeseries ?? [])

function formatCurrency(n: number) {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF', maximumFractionDigits: 0 }).format(n || 0)
}

const chartData = computed(() => {
  const labels = timeseries.value.map(e =>
    new Date(e.date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
  )
  return {
    labels,
    datasets: [
      { label: 'CA global', backgroundColor: 'rgba(59,130,246,0.15)', borderColor: '#3B82F6', fill: true, data: timeseries.value.map(e => e.ca_global), tension: 0.35 },
      { label: 'Ventes encaissées', backgroundColor: 'rgba(16,185,129,0.15)', borderColor: '#10B981', fill: false, data: timeseries.value.map(e => e.sales), tension: 0.35 },
      { label: 'Dettes en cours', backgroundColor: 'rgba(249,115,22,0.1)', borderColor: '#F97316', fill: false, data: timeseries.value.map(e => e.debts), tension: 0.35 },
    ],
  }
})

const chartOptions = {
  responsive: true, maintainAspectRatio: false,
  scales: { y: { ticks: { callback(v: any) { return typeof v === 'string' ? v : formatCurrency(Number(v)) } } } },
  plugins: {
    legend: { position: 'bottom' as const },
    tooltip: { callbacks: { label(c: any) { const v = c.parsed.y || 0; return `${c.dataset.label}: ${formatCurrency(v)}` } } },
  },
}

const refresh = () => loadMetrics()
</script>

<template>
  <div class="space-y-8 p-6">
    <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-blue-500 md:text-3xl">Tableau de bord</h1>
        <p class="text-sm text-gray-500">Vision instantanée du chiffre d'affaires global et des dettes en cours.</p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <select v-model="selectedPeriod" class="rounded-lg border px-3 py-2 text-sm shadow-sm">
          <option v-for="option in periodOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        <NuxtLink to="/dettes"
          class="inline-flex items-center rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white shadow hover:bg-blue-600">
          Gérer les dettes
        </NuxtLink>
        <button type="button"
          class="inline-flex items-center rounded-lg border border-blue-200 px-4 py-2 text-sm font-medium text-blue-500 hover:bg-blue-50"
          @click="refresh">
          Actualiser
        </button>
      </div>
    </div>

    <div v-if="isInitialLoading" class="rounded-xl bg-white p-8 text-center shadow-sm">
      <p class="animate-pulse text-sm text-gray-500">Chargement des indicateurs...</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <KpiCard class="dashboard-card" title="CA global" :value="formatCurrency(caGlobal)" icon="chart-bar"
        color="blue" />
      <KpiCard class="dashboard-card" title="Ventes encaissées" :value="formatCurrency(ventesEncaissees)"
        icon="currency-euro" color="green" />
      <KpiCard class="dashboard-card" title="Dettes en cours" :value="formatCurrency(dettesEnCours)" icon="credit-card"
        color="red" />
    </div>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <div class="dashboard-panel lg:col-span-2">
        <div class="mb-6 flex items-center justify-between gap-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-800">Tendance CA & dettes</h2>
            <p class="text-xs text-gray-500">Evolution quotidienne des ventes et dettes pour la période sélectionnée.
            </p>
          </div>
          <div v-if="lastUpdated" class="text-xs text-gray-400">
            Actualisé le {{ lastUpdated.toLocaleString('fr-FR') }}
          </div>
        </div>
        <div class="h-80">
          <Line v-if="timeseries.length" :data="chartData" :options="chartOptions" />
          <div v-else class="flex h-full items-center justify-center rounded-lg bg-slate-50 text-sm text-gray-500">
            Aucune donnée disponible pour la période sélectionnée.
          </div>
        </div>
      </div>

      <div class="dashboard-panel">
        <h2 class="mb-4 text-lg font-semibold text-slate-800">Top techniciens débiteurs</h2>
        <ul class="space-y-3">
          <li v-for="technician in topTechnicians" :key="technician.technician_name"
            class="flex items-center justify-between rounded-lg border border-slate-100 px-4 py-3">
            <div>
              <p class="font-medium text-slate-700">{{ technician.technician_name }}</p>
              <p class="text-xs text-gray-500">Montant dû</p>
            </div>
            <span class="text-sm font-semibold text-blue-500">{{ formatCurrency(technician.montant) }}</span>
          </li>
          <li v-if="!topTechnicians.length" class="text-sm text-gray-500">Aucun technicien en retard de paiement 🎉</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-card {
  @apply rounded-xl bg-white shadow-sm ring-1 ring-slate-100;
}

.dashboard-panel {
  @apply rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-100;
}
</style>
