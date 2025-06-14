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

  <div class="shadow-lg border rounded-md dark:border-gray-600 dark:shadow-gray-800 mt-3">
    <UTable :rows="facturesFiltrees" :columns="columns">
      <template #total-data="{ row }">{{ row.total }} FCFA</template>
      <template #verse-data="{ row }">{{ row.verse }} FCFA</template>
      <template #reste-data="{ row }">{{ row.reste }} FCFA</template>
      <!-- <template #produits-data="{ row }">
        <ul>
          <li v-for="produit in row.produits" :key="produit">{{ produit }}</li>
        </ul>
      </template> -->
      <!-- <template #actions-data="{ row }">
          <UButton color="blue" @click="nouveauVersement(row)">Versement</UButton>
        </template> -->
        <!-- Colonne personnalisée pour les actions -->
        <template #action-data="{ row }">
          <UButton color="blue" class="mr-2" @click="$emit('versement',row)">Versement</UButton>
          <UButton color="green" @click="$emit('voir',row)">voir</UButton>
        </template>
        <!-- Colonne personnalisée pour les actions -->
    </UTable>

    <div class="flex justify-end px-3 py-3.5 border-t border-gray-200 dark:border-gray-700">
      <UPagination v-model="page" :page-count="pageCount" :total="totalFactures" />
    </div>
    
  </div>
</template>
