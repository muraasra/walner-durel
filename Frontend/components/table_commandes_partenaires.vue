<script setup lang="ts">
import { ref, computed, watch } from "vue";
import selecteur_date from "./selecteur_date.vue";

interface Commande {
  id: number;
  date: string;
  partenaire: string;
  total: number;
  verse: number;
  reste: number;
  produits: string[];
}

const props = defineProps<{ commandes: Commande[] }>();

const columns = [
  { key: "date", label: "Date" },
  { key: "partenaire", label: "Partenaire" },
  { key: "total", label: "Montant Total" },
  { key: "verse", label: "Déjà Versé" },
  { key: "reste", label: "Reste à Payer" },
  { key: "produits", label: "Produits" },
];

const q = ref("");
const page = ref(1);
const pageCount = 10;
const statutSelectionne = ref<string[]>([]);
const plageDatesSelectionnee = ref<{ start: Date | null; end: Date | null }>({ start: null, end: null });

const commandesFiltrees = computed(() => {
  let liste = props.commandes;

  if (q.value) {
    liste = liste.filter((cmd) =>
      Object.values(cmd).some((valeur) =>
        String(valeur).toLowerCase().includes(q.value.toLowerCase())
      )
    );
  }

  if (plageDatesSelectionnee.value.start && plageDatesSelectionnee.value.end) {
    liste = liste.filter((cmd) => {
      const dateCommande = new Date(cmd.date);
      if (plageDatesSelectionnee.value.start && plageDatesSelectionnee.value.end){
        return dateCommande >= plageDatesSelectionnee.value.start && dateCommande <= plageDatesSelectionnee.value.end;
      } else {
        return false ; 
      }
      
    });
  }


  return liste.slice((page.value - 1) * pageCount, page.value * pageCount);
});

const totalCommandes = computed(() => props.commandes.length);

const resetFiltres = () => {
  q.value = "";
  statutSelectionne.value = [];
};

watch([q, statutSelectionne], () => {
  page.value = 1;
});
</script>

<template>
  <div class="flex flex-col lg:flex-row justify-between items-center w-full py-3.5 border-b border-gray-200 dark:border-gray-700 gap-4">
    <UInput v-model="q" placeholder="Rechercher une commande..." class="w-full lg:w-[250px]" color="blue" variant="outline" />

    <div class="flex items-center gap-3">
      <selecteur_date class="w-full" @update-range="(range) => (plageDatesSelectionnee = range)" />
      <UButton @click="resetFiltres" color="gray">Réinitialiser</UButton>
    </div>
  </div>

  <div class="shadow-lg border rounded-md dark:border-gray-600 dark:shadow-gray-800">
    <UTable :rows="commandesFiltrees" :columns="columns">
      <template #total-data="{ row }">{{ row.total }} FCFA</template>
      <template #verse-data="{ row }">{{ row.verse }} FCFA</template>
      <template #reste-data="{ row }">{{ row.reste }} FCFA</template>
      <template #produits-data="{ row }">
        <ul>
          <li v-for="produit in row.produits" :key="produit">{{ produit }}</li>
        </ul>
      </template>
    </UTable>

    <div class="flex justify-end px-3 py-3.5 border-t border-gray-200 dark:border-gray-700">
      <UPagination v-model="page" :page-count="pageCount" :total="totalCommandes" />
    </div>
  </div>
</template>
