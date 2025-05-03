<!-- <script setup lang="ts">
import  {ref , computed , watch} from "vue";
import { PRODUCTS_DATA } from "~/constants";
import selecteur_date from "./selecteur_date.vue";

const columns = [
  {
    key: "codeCommande",
    label: "Code Commande",
  },
  {
    key: "nomClient",
    label: "Nom du Client",
  },
  {
    key: "lieuCommande",
    label: "Lieu de Commande",
  },
  {
    key: "imageProduit",
    label: "Image",
  },
  {
    key: "nomProduit",
    label: "Nom du Produit",
  },
  {
    key: "dateCommande",
    label: "Date de Commande",
  },
  {
    key: "prix",
    label: "Prix",
  },
  {
    key: "quantiteCommandee",
    label: "Quantité",
  },
  {
    key: "statut",
    label: "Statut",
  },
];

const produits = PRODUCTS_DATA.map((p, i) => ({
  codeCommande: `CMD-${i + 1}`,
  nomClient: p.nomClient,
  nomProduit: p.nomProduit,
  lieuCommande: p.lieuCommande,
  imageProduit: p.imageProduit,
  dateCommande: p.dateCommande,
  prix: p.prix,
  quantiteCommandee: p.quantiteCommandee,
  statut: p.statut,
}));

// Filtres
const statutsCommande = [
  { key: "Livré", label: "Livré", value: "Livré" },
  { key: "En cours", label: "En cours", value: "En cours" },
  { key: "Retour", label: "Retour", value: "Retour" },
  { key: "Annulé", label: "Annulé", value: "Annulé" },
];

const q = ref("");
const page = ref(1);
const pageCount = 15;
const statutSelectionne = ref<
  Array<{ key: string; label: string; value: string }>
>([]);
const plageDatesSelectionnee = ref<{ 
    start: Date | null; 
    end: Date | null 
}>({start: null, end: null,});

const lignesFiltrees = computed(() => {
  let produitsFiltres = produits;

  // Filtre par statut
  if (statutSelectionne.value.length) {
    produitsFiltres = produitsFiltres.filter((produit) =>
      statutSelectionne.value.some((statut) => statut.value === produit.statut)
    );
  }

  // Filtre par recherche
  if (q.value) {
    produitsFiltres = produitsFiltres.filter((produit) =>
      Object.values(produit).some((valeur) =>
        String(valeur).toLowerCase().includes(q.value.toLowerCase())
      )
    );
  }

  // Filtre par plage de dates
  if (plageDatesSelectionnee.value.start && plageDatesSelectionnee.value.end) {
    produitsFiltres = produitsFiltres.filter((produit) => {
      const dateCommande = new Date(produit.dateCommande);
      if (plageDatesSelectionnee.value.start && plageDatesSelectionnee.value.end) {
        return (
        dateCommande >= plageDatesSelectionnee.value.start &&
        dateCommande <= plageDatesSelectionnee.value.end
      );
      } else{
        return false;
      }

    });
  }

  // Appliquer la pagination
  return produitsFiltres.slice(
    (page.value - 1) * pageCount,
    page.value * pageCount
  );
});

const totalProduitsFiltres = computed(() => {
  let produitsFiltres = produits;

  if (statutSelectionne.value.length) {
    produitsFiltres = produitsFiltres.filter((produit) =>
      statutSelectionne.value.some((statut) => statut.value === produit.statut)
    );
  }

  if (q.value) {
    produitsFiltres = produitsFiltres.filter((produit) =>
      Object.values(produit).some((valeur) =>
        String(valeur).toLowerCase().includes(q.value.toLowerCase())
      )
    );
  }

  if (plageDatesSelectionnee.value.start && plageDatesSelectionnee.value.end) {
    produitsFiltres = produitsFiltres.filter((produit) => {
      const dateCommande = new Date(produit.dateCommande);
      if(plageDatesSelectionnee.value.start && plageDatesSelectionnee.value.end) {
        return (
        dateCommande >= plageDatesSelectionnee.value.start &&
        dateCommande <= plageDatesSelectionnee.value.end
      );
      } else {
        return false;
      }

    });
  }

  return produitsFiltres.length;
});

const resetFiltres = () => {
  statutSelectionne.value = [];
  q.value = "";
};

watch([q, statutSelectionne], () => {
  page.value = 1;
});
</script>

<template>
  <div
    class="flex flex-col lg:flex-row justify-between items-center w-full py-3.5 border-b border-gray-200 dark:border-gray-700 gap-4"
  >
    <UInput color="blue" variant="outline" v-model="q" placeholder="Rechercher une commande..." class="w-full lg:w-[250px] "   />

    <div class="w-full flex lg:items-center flex-col lg:flex-row gap-3">
      <selecteur_date
        class="w-full"
        @update-range="
          (range) => {
            plageDatesSelectionnee.start = range.start;
            plageDatesSelectionnee.end = range.end;
          }
        "
      />
      <div class="flex items-center gap-3">
        <USelectMenu
          color="blue" 
          variant="outline"
          v-model="statutSelectionne"
          :options="statutsCommande"
          multiple
          placeholder="Statut"
          class="w-40"
        />
        <UButton @click="resetFiltres" color="gray">Réinitialiser</UButton>
      </div>
    </div>
  </div>

  <div class="shadow-lg border rounded-md dark:border-gray-600 dark:shadow-gray-800">
    <div>
      <UTable
        :rows="lignesFiltrees"
        :columns="columns"
        class="w-[270px] sm:w-[320px] md:w-[490px] lg:w-full overflow-x-auto"
      >
        <template #imageProduit-data="{ row }">
          <img :src="row.imageProduit" :alt="row.nomProduit" class="w-[100px] h-[60px]" />
        </template>

        <template #statut-data="{ row }">
          <span
            :class="{
              'text-[#00B69B] bg-[#00B69B]/10 px-2 py-1.5 rounded-md': row.statut === 'Livré',
              'text-[#FFA756] bg-[#FFA756]/10 px-2 py-1.5 rounded-md': row.statut === 'En cours',
              'text-[#BA29FF] bg-[#BA29FF]/10 px-2 py-1.5 rounded-md': row.statut === 'Retour',
              'text-[#EF3826] bg-[#EF3826]/10 px-2 py-1.5 rounded-md': row.statut === 'Annulé',
            }"
          >
            {{ row.statut }}
          </span>
        </template>
      </UTable>

      <div class="flex justify-end px-3 py-3.5 border-t border-gray-200 dark:border-gray-700">
        <UPagination v-model="page" :page-count="pageCount" :total="totalProduitsFiltres" />
      </div>
    </div>
  </div>
</template> -->


<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { PRODUCTS_DATA } from "~/constants";
import selecteur_date from "./selecteur_date.vue";

const columns = [
  { key: "codeCommande", label: "Code Commande" },
  { key: "nomClient", label: "Nom du Client" },
  { key: "lieuCommande", label: "Lieu de Commande" },
  { key: "imageProduit", label: "Image" },
  { key: "nomProduit", label: "Nom du Produit" },
  { key: "dateCommande", label: "Date de Commande" },
  { key: "prix", label: "Prix" },
  { key: "quantiteCommandee", label: "Quantité" },
  { key: "statut", label: "Statut" },
];

const produits = PRODUCTS_DATA.map((p, i) => ({
  codeCommande: `CMD-${i + 1}`,
  nomClient: p.nomClient,
  nomProduit: p.nomProduit,
  lieuCommande: p.lieuCommande,
  imageProduit: p.imageProduit,
  dateCommande: p.dateCommande,
  prix: p.prix,
  quantiteCommandee: p.quantiteCommandee,
  statut: p.statut,
  estPartenaire: p.estPartenaire ?? false,
}));

// Filtrer uniquement les commandes des clients (non partenaires)
const commandesClients = computed(() => {
  return produits.filter((produit) => !produit.estPartenaire);
});

const statutsCommande = [
  { key: "Livré", label: "Livré", value: "Livré" },
  { key: "En cours", label: "En cours", value: "En cours" },
  { key: "Retour", label: "Retour", value: "Retour" },
  { key: "Annulé", label: "Annulé", value: "Annulé" },
];

const q = ref("");
const page = ref(1);
const pageCount = 15;
const statutSelectionne = ref<Array<{ key: string; label: string; value: string }>>([]);
const plageDatesSelectionnee = ref<{ start: Date | null; end: Date | null }>({ start: null, end: null });

const lignesFiltrees = computed(() => {
  let produitsFiltres = commandesClients.value;

  if (statutSelectionne.value.length) {
    produitsFiltres = produitsFiltres.filter((produit) =>
      statutSelectionne.value.some((statut) => statut.value === produit.statut)
    );
  }

  if (q.value) {
    produitsFiltres = produitsFiltres.filter((produit) =>
      Object.values(produit).some((valeur) =>
        String(valeur).toLowerCase().includes(q.value.toLowerCase())
      )
    );
  }

  if (plageDatesSelectionnee.value.start && plageDatesSelectionnee.value.end) {
    produitsFiltres = produitsFiltres.filter((produit) => {
      const dateCommande = new Date(produit.dateCommande);
      if (plageDatesSelectionnee.value.start && plageDatesSelectionnee.value.end) {
        return (
        dateCommande >= plageDatesSelectionnee.value.start &&
        dateCommande <= plageDatesSelectionnee.value.end
      );
      } else{
        return false;
      }

    });
  }

  return produitsFiltres.slice((page.value - 1) * pageCount, page.value * pageCount);
});

const totalProduitsFiltres = computed(() => lignesFiltrees.value.length);
const resetFiltres = () => {
  statutSelectionne.value = [];
  q.value = "";
};
watch([q, statutSelectionne], () => {
  page.value = 1;
});
</script>

<template>
  <div class="flex flex-col lg:flex-row justify-between items-center w-full py-3.5 border-b border-gray-200 dark:border-gray-700 gap-4">
    <UInput v-model="q" placeholder="Rechercher une commande..." class="w-full lg:w-[250px]" />
    <div class="w-full flex lg:items-center flex-col lg:flex-row gap-3">
      <selecteur_date @update-range="(range) => (plageDatesSelectionnee = range)" class="w-full" />
      <div class="flex items-center gap-3">
        <USelectMenu v-model="statutSelectionne" :options="statutsCommande" multiple placeholder="Statut" class="w-40" />
        <UButton @click="resetFiltres" color="gray">Réinitialiser</UButton>
      </div>
    </div>
  </div>

  <div class="shadow-lg border rounded-md dark:border-gray-600 dark:shadow-gray-800">
    <UTable :rows="lignesFiltrees" :columns="columns" class="overflow-x-auto">
      <template #imageProduit-data="{ row }">
        <img :src="row.imageProduit" :alt="row.nomProduit" class="w-[100px] h-[60px]" />
      </template>
      <template #statut-data="{ row }">
        <span
          :class="{
            'text-[#00B69B] bg-[#00B69B]/10 px-2 py-1.5 rounded-md': row.statut === 'Livré',
            'text-[#FFA756] bg-[#FFA756]/10 px-2 py-1.5 rounded-md': row.statut === 'En cours',
            'text-[#BA29FF] bg-[#BA29FF]/10 px-2 py-1.5 rounded-md': row.statut === 'Retour',
            'text-[#EF3826] bg-[#EF3826]/10 px-2 py-1.5 rounded-md': row.statut === 'Annulé',
          }"
        >
          {{ row.statut }}
        </span>
      </template>
    </UTable>

    <div class="flex justify-end px-3 py-3.5 border-t border-gray-200 dark:border-gray-700">
      <UPagination v-model="page" :page-count="pageCount" :total="totalProduitsFiltres" />
    </div>
  </div>
</template>

