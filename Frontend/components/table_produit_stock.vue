<script setup lang="ts">
import { ref, computed } from "vue";
import { PRODUCTS_DATA } from "~/constants";

const colonnes = [
  {
    key: "reference",
    label: "Référence",
  },
  
  {
    key: "description",
    label: "Description",
  },
  
  {
    key: "nomProduit",
    label: "Nom",
  },
  {
    key: "categorie",
    label: "Catégorie",
  },

  {
    key: "prix",
    label: "Prix (FCFA)",
  },
  
  {
    key: "quantiteTotale",
    label: "Quantité",
  },
  {
    key: "statut",
    label: "Statut",
  },
 
];


let produits = [];
(async () => {
  try {
    const { data, error } = await useApi('http://127.0.0.1:8000/api/produits/', {
      method: 'GET',
      server: false
    });

    if (error.value) {
      console.error("Erreur API :", error.value);
    }

    produits = Array.isArray(data.value)
      ? data.value.map(p => ({
          reference: p.reference,
          nomProduit: p.nom,
          categorie: p.category,
          prix: p.prix,
          description: p.description,
          quantiteTotale: p.quantite,
          statut: p.actif ? "Disponible" : "Non disponible",
        }))
      : [];
  } catch (err) {
    console.error("Erreur lors de l'appel API :", err);
  }
})();


const q = ref("");
const page = ref(1);
const pageCount = 15;

const lignesFiltrees = computed(() => {
  let produitsFiltres = produits;

  // Appliquer la recherche
  if (q.value) {
    produitsFiltres = produitsFiltres.filter((produit) =>
      Object.values(produit).some((valeur) =>
        String(valeur).toLowerCase().includes(q.value.toLowerCase())
      )
    );
  }

  // Appliquer la pagination
  return produitsFiltres.slice(
    (page.value - 1) * pageCount,
    page.value * pageCount
  );
});

const totalProduitsFiltres = computed(() => {
  let produitsFiltres = produits;

  // Appliquer la recherche
  if (q.value) {
    produitsFiltres = produitsFiltres.filter((produit) =>
      Object.values(produit).some((valeur) =>
        String(valeur).toLowerCase().includes(q.value.toLowerCase())
      )
    );
  }

  return produitsFiltres.length;
});
</script>

<template>
  <div
    class="flex justify-between items-center w-full py-3.5 border-b border-gray-200 dark:border-gray-700"
  >
    <UInput color="blue" variant="outline" v-model="q" placeholder="Rechercher un produit..." />
  </div>
  <div
    class="shadow-lg border rounded-md dark:border-gray-600 dark:shadow-gray-800"
  >
    <div>
      <UTable
        :rows="lignesFiltrees"
        :columns="colonnes"
        class="w-[270px] sm:w-[320px] md:w-[490px] lg:w-full overflow-x-auto"
      >
       <!-- <template #imageProduit-data="{ row }">
          <img
            :src="row.imageProduit"
            :alt="row.nomProduit"
            class="w-[140px] h-[90px]"
          />
        </template>-->
        <template #prix-data="{ row }">
          <span>{{ row.prix }} </span>
        </template>
        <!--<template #couleursDisponibles-data="{ row }">
          <div class="flex items-center gap-x-1">
            <span
              v-for="couleur in row.couleursDisponibles"
              class="rounded-full size-4"
              :style="{ backgroundColor: couleur }"
            />
          </div>
        </template>-->
      </UTable>

      <div
        class="flex justify-end px-3 py-3.5 border-t border-gray-200 dark:border-gray-700"
      >
        <UPagination
          :active-button="{ variant: 'outline' }"
          :inactive-button="{ color: 'blue' }"
          v-model="page"
          color="blue" 
          :page-count="pageCount"
          :total="totalProduitsFiltres"
          
        />
      </div>
    </div>
  </div>
</template>
