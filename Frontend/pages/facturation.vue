<!-- <script setup lang="ts">
import { ref, computed } from "vue";

interface Produit {
  id: number;
  nom: string;
  prix: number;
  quantite: number;
}

const panier = ref<Produit[]>([]);

// Ajouter un produit au panier
const ajouterAuPanier = (produit: Produit) => {
  const index = panier.value.findIndex((p) => p.id === produit.id);
  if (index !== -1) {
    panier.value[index].quantite += 1;
  } else {
    panier.value.push({ ...produit, quantite: 1 });
  }
};

// Supprimer un produit du panier
const retirerDuPanier = (id: number) => {
  panier.value = panier.value.filter((p) => p.id !== id);
};

// Calcul du total du panier
const totalPanier = computed(() => {
  return panier.value.reduce((total, produit) => total + produit.prix * produit.quantite, 0);
});

// Formatage en FCFA
const formatMontant = (montant: number) => {
  return new Intl.NumberFormat("fr-CM", { style: "currency", currency: "XAF" }).format(montant);
};
</script>

<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">Facturation</h2>

    //Champ de recherche pour trouver un produit 
    <input
      type="text"
      placeholder="Rechercher un produit..."
      class="border p-2 w-full rounded mb-4"
      v-model="recherche"
    />

    //Liste des produits (simulation) 
    <ul>
      <li v-for="produit in produitsFiltrés" :key="produit.id" class="flex justify-between border-b p-2">
        <span>{{ produit.nom }} - {{ formatMontant(produit.prix) }}</span>
        <button @click="ajouterAuPanier(produit)" class="bg-blue-500 text-white px-3 py-1 rounded">Ajouter</button>
      </li>
    </ul>

    // Affichage du panier 
    <h3 class="text-xl font-semibold mt-6">Panier</h3>
    <ul v-if="panier.length">
      <li v-for="produit in panier" :key="produit.id" class="flex justify-between border-b p-2">
        <span>{{ produit.nom }} (x{{ produit.quantite }})</span>
        <span>{{ formatMontant(produit.prix * produit.quantite) }}</span>
        <button @click="retirerDuPanier(produit.id)" class="bg-red-500 text-white px-3 py-1 rounded">Supprimer</button>
      </li>
    </ul>
    <p v-else class="text-gray-500">Le panier est vide.</p>

    //Total
    <h3 class="text-lg font-semibold mt-4">Total : {{ formatMontant(totalPanier) }}</h3>
  </div>
</template> -->


<script setup lang="ts">
import { ref, computed } from "vue";

interface InvoiceItem {
  id: number;
  description: string;
  quantity: number;
  price: number;
}

interface Invoice {
  number: string;
  date: string;
  clientName: string;
  clientEmail: string;
  items: InvoiceItem[];
  taxRate: number;
}

const invoice = ref<Invoice>({
  number: "",
  date: new Date().toISOString().split("T")[0],
  clientName: "",
  clientEmail: "",
  items: [],
  taxRate: 10,
});

const invoicePreview = ref<HTMLElement | null>(null);

const addItem = () => {
  invoice.value.items.push({
    id: Date.now(),
    description: "",
    quantity: 1,
    price: 0,
  });
};

const removeItem = (index: number) => {
  invoice.value.items.splice(index, 1);
};

const subtotal = computed(() => {
  return invoice.value.items.reduce(
    (sum, item) => sum + item.quantity * item.price,
    0
  );
});

const taxAmount = computed(() => {
  return subtotal.value * (invoice.value.taxRate / 100);
});

const total = computed(() => {
  return subtotal.value + taxAmount.value;
});

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "XAF",
  }).format(amount);
};

const printInvoice = () => {
  const printContents = invoicePreview.value?.innerHTML;
  const originalContents = document.body.innerHTML;

  document.body.innerHTML = printContents || "";
  window.print();
  document.body.innerHTML = originalContents;
};
</script>

<template>
  <section class="mt-5 px-6">
    <h2 class="text-xl md:text-3xl font-bold text-blue-400">Factures</h2>
    <div
      class="mt-7 border mx-auto dark:border-gray-600 dark:shadow-gray-800 shadow-xl rounded-lg overflow-hidden"
    >
      <div class="px-6 py-4 sm:p-6">
        <div
          class="w-full grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6 mb-6"
        >
          <div class="sm:col-span-3">
            <label
              for="invoiceNumber"
              class="block text-sm font-medium text-gray-700 dark:text-gray-200"
              >Numéro de la Facture</label
            >
            <UInput
              id="invoiceNumber"
              color = "blue"
              variant = "outline"
              v-model="invoice.number"
              class="mt-1"
              placeholder="Numéro de la facture"
            />
          </div>
          <div class="sm:col-span-3">
            <label
              for="invoiceDate"
              class="block text-sm font-medium text-gray-700 dark:text-gray-200"
              >Date de la Facture</label
            >
            <UInput
              id="invoiceDate"
              color = "blue"
              variant = "outline"
              v-model="invoice.date"
              class="mt-1"
              placeholder="Date de la facture"
              type="date"
            />
          </div>
          <div class="sm:col-span-3">
            <label
              for="clientName"
              class="block text-sm font-medium text-gray-700 dark:text-gray-200"
              >Nom du Client</label
            >
            <UInput
              id="clientName"
              color = "blue"
              variant = "outline"
              v-model="invoice.clientName"
              class="mt-1"
              placeholder="Nom du client"
            />
          </div>
          <div class="sm:col-span-3">
            <label
              for="clientEmail"
              class="block text-sm font-medium text-gray-700 dark:text-gray-200"
              >Email du Client</label
            >
            <UInput
              id="clientEmail"
              color ="blue"
              variant ="outline"
              v-model="invoice.clientEmail"
              class="mt-1"
              type="email"
              placeholder="Email du client"
            />
          </div>
        </div>

        <!-- Invoice Items -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-blue-400 mb-3">
            Articles de la Facture
          </h2>
          <div
            v-for="(item, index) in invoice.items"
            :key="index"
            class="flex flex-wrap sm:flex-nowrap items-center space-y-2 sm:space-y-0 sm:space-x-4 mb-4"
          >
            <UInput
              v-model="item.description"
              color ="blue"
              variant="outline"
              placeholder="Description"
              class="flex-grow w-full sm:w-auto"
            />
            <UInput
              type="number"
              color ="blue"
              variant="outline"
              v-model="item.quantity"
              placeholder="Quantité"
              class="w-full sm:w-28"
            />
            <UInput
              type="number"
              color ="blue"
              variant="outline"
              v-model="item.price"
              placeholder="Prix"
              class="w-full sm:w-28"
            />
            <UButton
              icon="i-heroicons-trash"
              @click="removeItem(index)"
              color="red"
              class="w-full flex items-center justify-center sm:w-auto"
            >
            </UButton>
          </div>
          <UButton
            @click="addItem"
            color="blue"
            variant="solid"
            size="lg"
            icon="i-heroicons-plus"
            class="w-full flex items-center justify-center sm:w-auto"
          >
            Ajouter un article
          </UButton>
        </div>

        <!-- Totals -->
        <div class="mb-6">
          <div
            class="flex justify-between items-center py-2 border-t border-gray-200 dark:border-gray-600"
          >
            <span class="text-sm font-medium text-gray-500 dark:text-gray-300"
              >Sous-total :</span
            >
            <span
              class="text-sm font-medium text-gray-900 dark:text-gray-100"
              >{{ formatCurrency(subtotal) }}</span
            >
          </div>
          <div
            class="flex justify-between items-center py-2 border-t border-gray-200 dark:border-gray-600"
          >
            <span class="text-sm font-medium text-gray-500 dark:text-gray-300"
              >Taxe ({{ invoice.taxRate }}%):</span
            >
            <span
              class="text-sm font-medium text-gray-900 dark:text-gray-100"
              >{{ formatCurrency(taxAmount) }}</span
            >
          </div>
          <div
            class="flex justify-between items-center py-2 border-t border-b border-gray-200 dark:border-gray-600"
          >
            <span class="text-base font-medium text-gray-900 dark:text-gray-100"
              >Total :</span
            >
            <span
              class="text-base font-medium text-gray-900 dark:text-gray-100"
              >{{ formatCurrency(total) }}</span
            >
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-4">
          <UButton 
            @click="printInvoice" 
            size="lg" 
            icon="i-heroicons-printer"
            color = "blue"
            variant ="solid"
            >
            Imprimer la Facture
          </UButton>
        </div>
      </div>
    </div>

    <!-- Invoice Preview (for printing) -->
    <div
      ref="invoicePreview"
      class="hidden bg-white p-8 max-w-4xl mx-auto mt-8"
    >
      <h1 class="text-3xl font-bold mb-6">Facture</h1>
      <div class="mb-6">
        <p><strong>Numéro de la Facture :</strong> {{ invoice.number }}</p>
        <p><strong>Date :</strong> {{ invoice.date }}</p>
        <p><strong>Client :</strong> {{ invoice.clientName }}</p>
        <p><strong>Email :</strong> {{ invoice.clientEmail }}</p>
      </div>
      <table class="w-full mb-6">
        <thead>
          <tr>
            <th class="text-left">Description</th>
            <th class="text-right">Quantité</th>
            <th class="text-right">Prix</th>
            <th class="text-right">Total</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in invoice.items" :key="item.id">
            <td>{{ item.description }}</td>
            <td class="text-right">{{ item.quantity }}</td>
            <td class="text-right">{{ formatCurrency(item.price) }}</td>
            <td class="text-right">
              {{ formatCurrency(item.quantity * item.price) }}
            </td>
          </tr>
        </tbody>
      </table>
      <div class="mb-6">
        <p><strong>Sous-total :</strong> {{ formatCurrency(subtotal) }}</p>
        <p>
          <strong>Taxe ({{ invoice.taxRate }}%):</strong>
          {{ formatCurrency(taxAmount) }}
        </p>
        <p><strong>Total :</strong> {{ formatCurrency(total) }}</p>
      </div>
    </div>
  </section>
</template>
