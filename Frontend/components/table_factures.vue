<script setup lang="ts">
import { ref, computed, watch } from "vue";
import selecteur_date from "./selecteur_date.vue";

interface Facture {
  id: number;
  numero: string;
  date: string;
  nom: string;
  total: number;
  verse: number;
  reste: number;
  type: string;
  status:string;

}

const props = defineProps<{ factures: Facture[] }>();

const columns = 
[
  { key: "numero", label: "Numero Facture" },
  { key: "date", label: "Date" },
  { key: "type", label: "Type" },
  { key: "nom", label: "Nom" },
  { key: "status", label: "Status" },
  { key: "total", label: "Montant Total" },
  { key: "verse", label: "Déjà Versé" },
  { key: "reste", label: "Reste à Payer" },
  { key: "action", label: "Actions" },
];

const q = ref("");
const page = ref(1);
const pageCount = 10;
const plageDatesSelectionnee = ref<{ start: Date | null; end: Date | null }>({ start: null, end: null });

const facturesFiltrees = computed(() => {
  let liste = props.factures;

  if (q.value) {
    liste = liste.filter((fact) =>
      Object.values(fact).some((val) =>
        String(val).toLowerCase().includes(q.value.toLowerCase())
      )
    );
  }

  if (plageDatesSelectionnee.value.start && plageDatesSelectionnee.value.end) {
    liste = liste.filter((fact) => {
      const dateFacture = new Date(fact.date);
      return (
        dateFacture >= plageDatesSelectionnee.value.start! &&
        dateFacture <= plageDatesSelectionnee.value.end!
      );
    });
  }

  return liste.slice((page.value - 1) * pageCount, page.value * pageCount);
});

const totalFactures = computed(() => props.factures.length);

const resetFiltres = () => {
  q.value = "";
  plageDatesSelectionnee.value = { start: null, end: null };
};

watch([q, plageDatesSelectionnee], () => {
  page.value = 1;
});
</script>

<template>
  <div class="flex flex-col lg:flex-row justify-between items-center w-full py-3.5 border-b border-gray-200 dark:border-gray-700 gap-4">
    <UInput v-model="q" placeholder="Rechercher une facture..." class="w-full lg:w-[250px]" color="blue" variant="outline" />
    <div class="flex items-center gap-3">
      <selecteur_date class="w-full" @update-range="(range) => (plageDatesSelectionnee = range)" />
      <UButton @click="resetFiltres" color="gray">Réinitialiser</UButton>
    </div>
  </div>

  <div class="shadow border rounded-xl bg-white mt-3">
    <UTable
      :rows="facturesFiltrees"
      :columns="columns"
      class="min-w-full text-sm border-separate border-spacing-0"
      :thead-class="'bg-gray-50 text-base font-semibold text-gray-700'"
      :tbody-class="''"
  :row-class="(row: any, rowIndex: number) => rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50 hover:bg-gray-100 transition'"
    >
      <template #numero-data="{ row }">
        <span class="font-medium text-gray-800">{{ row.numero }}</span>
      </template>
      <template #date-data="{ row }">
        <span class="text-gray-700">{{ new Date(row.date).toLocaleString('fr-FR', {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'}).replace(',', '') }}</span>
      </template>
      <template #type-data="{ row }">
        <span class="text-gray-700">{{ row.type }}</span>
      </template>
      <template #nom-data="{ row }">
        <span class="text-gray-700">{{ row.nom }}</span>
      </template>
      <template #status-data="{ row }">
        <span
          :class="[
            'inline-block px-3 py-1 text-xs font-semibold rounded-full',
            row.status === 'payé'
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'
          ]"
        >
          {{ row.status }}
        </span>
      </template>
      <template #total-data="{ row }">
        <span class="font-semibold text-gray-900">{{ row.total }} FCFA</span>
      </template>
      <template #verse-data="{ row }">
        <span class="font-semibold text-green-700">{{ row.verse }} FCFA</span>
      </template>
      <template #reste-data="{ row }">
        <span :class="row.reste > 0 ? 'font-semibold text-orange-600' : 'font-semibold text-green-600'">{{ row.reste }} FCFA</span>
      </template>
      <template #action-data="{ row }">
        <UButton
          v-if="row.reste > 0 && row.status !== 'payé'"
          color="blue"
          variant="outline"
          size="sm"
          class="mr-2"
          @click="$emit('versement', row)"
        >
          Versement
        </UButton>
        <UButton color="green" variant="outline" size="sm" @click="$emit('voir', row)">Voir</UButton>
      </template>
    </UTable>

    <div class="flex justify-end px-3 py-3.5 border-t border-gray-200">
      <UPagination v-model="page" :page-count="pageCount" :total="totalFactures" />
    </div>
  </div>
</template>
