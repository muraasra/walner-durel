<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useApi } from "../stores/useApi"; // Assure-toi que ce chemin est correct

// Colonnes du tableau
const colonnes = [
  { key: "reference", label: "Référence" },
  { key: "description", label: "Description" },
  { key: "nomProduit", label: "Nom" },
  { key: "category", label: "Catégorie" },
  { key: "prix", label: "Prix (FCFA)" },
  { key: "quantiteTotale", label: "Quantité" },
  { key: "statut", label: "Statut" },
];

// Interface produit
interface Product {
  id: number;
  reference: string;
  nomProduit: string;
  category: string;
  prix: number;
  description: string;
  quantiteTotale: number;
  statut: boolean;
  boutique: number;
}

// Liste des produits (réactif)
const produits = ref<Product[]>([]);

// 🔍 Recherche + pagination
const q = ref("");
const page = ref(1);
const pageCount = 15;

// Chargement des produits depuis l'API
async function chargementProduits() {
  try {
    const { data, error } = await useApi<Product[]>("http://127.0.0.1:8000/api/produits/", {
      method: "GET",
      server: false,
    });

    if (error.value) {
      console.error("Erreur API :", error.value);
      return;
    }

    produits.value = Array.isArray(data.value)
      ? data.value.map((p: any) => ({
          id: p.id,
          reference: p.reference,
          nomProduit: p.nom,
          category: p.category,
          prix: p.prix,
          description: p.description,
          quantiteTotale: p.quantite,
          statut: p.actif,
          boutique: p.boutique,
        }))
      : [];
  } catch (err) {
    console.error("Erreur lors de l'appel API :", err);
  }
}

onMounted(() => {
  chargementProduits();
});

// Produits filtrés (par recherche)
const lignesFiltrees = computed(() => {
  let produitsFiltres = produits.value;

  if (q.value) {
    produitsFiltres = produitsFiltres.filter((produit: Product) =>
      Object.values(produit).some((valeur) =>
        String(valeur).toLowerCase().includes(q.value.toLowerCase())
      )
    );
  }

  return produitsFiltres.slice(
    (page.value - 1) * pageCount,
    page.value * pageCount
  );
});

// Total pour pagination
const totalProduitsFiltres = computed(() => {
  let produitsFiltres = produits.value;

  if (q.value) {
    produitsFiltres = produitsFiltres.filter((produit: Product) =>
      Object.values(produit).some((valeur) =>
        String(valeur).toLowerCase().includes(q.value.toLowerCase())
      )
    );
  }

  return produitsFiltres.length;
});
</script>

<template>
  <div class="space-y-4">
    <!-- Barre de recherche -->
    <div class="flex justify-between items-center w-full py-3.5 border-b border-gray-200 dark:border-gray-700">
      <UInput
        color="blue"
        variant="outline"
        v-model="q"
        placeholder="Rechercher un produit..."
      />
    </div>

    <!-- Tableau -->
    <div class="shadow-lg border rounded-md dark:border-gray-600 dark:shadow-gray-800">
      <UTable
        :rows="lignesFiltrees"
        :columns="colonnes"
        class="w-[270px] sm:w-[320px] md:w-[490px] lg:w-full overflow-x-auto"
      >
        <!-- Prix personnalisé -->
        <template #prix-data="{ row }">
          <span>{{ row.prix }} FCFA</span>
        </template>
      </UTable>

      <!-- Pagination -->
      <div class="flex justify-end px-3 py-3.5 border-t border-gray-200 dark:border-gray-700">
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
