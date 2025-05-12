<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useNotification } from '../types/useNotification';

interface InvoiceItem {
  id: number;
  reference: string;
  name: string;
  description: string;
  quantity: number;
  price: number;
}

interface Invoice {
  number: string;
  date: string;
  recipientType: "client" | "partenaire" | "";
  client: {
    nom: string;
    prenom: string;
    telephone: string;
  };
  partenaire: string;
  items: InvoiceItem[];
  taxRate: number;
  montantVerse: number; 
}

// Interface correspondant à la structure de votre API
interface Product {
  reference: string;
  nom: string;         
  description: string;
  prix: number;        
  category?: string;   
  quantite?: number;   
  actif?: boolean;    
}

interface Partner {
  id?: number;
  nom: string;
  prenom: string;
  telephone: string;
  localisation?: string;
  statut?: string;
  dateadhesion?: string;
  boutique?: string;
}

// Récupération des produits depuis l'API
const products = ref<Product[]>([]);
const fetchProducts = async () => {
  try {
    const { data, error } = await useApi('http://127.0.0.1:8000/api/produits/', {
      method: 'GET',
      server: false
    });
    
    if (error.value) {
      console.error("Erreur lors de la récupération des produits:", error.value);
      return;
    }
    
    // Mappez les données de l'API vers  Product
    products.value = Array.isArray(data.value) 
      ? data.value.map(p => ({
          reference: p.reference,
          nom: p.nom,
          description: p.description,
          prix: p.prix,
          category: p.category,
          quantite: p.quantite,
          actif: p.actif
        }))
      : [];
      
  } catch (err) {
    console.error("Erreur inattendue:", err);
  }
};

// Récupération des partenaires depuis l'API
const partners = ref<Partner[]>([]);
const fetchPartners = async () => {
  try {
    const { data, error } = await useApi('http://127.0.0.1:8000/api/partenaires/', {
      method: 'GET',
      server: false
    });
    
    if (error.value) {
      console.error("Erreur lors de la récupération des partenaires:", error.value);
      return;
    }
    
    // Mappez les données de l'API vers Partner
    partners.value = Array.isArray(data.value) ? data.value : [];
      
  } catch (err) {
    console.error("Erreur inattendue:", err);
  }
};

const invoice = ref<Invoice>({
  number: generateInvoiceNumber(),
  date: new Date().toISOString().split("T")[0],
  recipientType: "",
  client: {
    nom: "",
    prenom: "",
    telephone: "",
  },
  partenaire: "",
  items: [],
  taxRate: 10,
  montantVerse: 0, // Initialisation du montant versé à 0
});

const currentProductRef = ref("");
const invoicePreview = ref<HTMLElement | null>(null);

function generateInvoiceNumber(): string {
  const prefix = "FACT";
  const date = new Date();
  const year = date.getFullYear().toString().slice(-2);
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const randomPart = Math.floor(Math.random() * 10000)
    .toString()
    .padStart(4, "0");
  return `${prefix}-${year}${month}-${randomPart}`;
}

const findProductByReference = (reference: string): Product | undefined => {
  return products.value.find((product) => product.reference === reference);
};

const addItem = () => {
  const product = findProductByReference(currentProductRef.value);
  if (product) {
    invoice.value.items.push({
      id: Date.now(),
      reference: product.reference,
      name: product.nom,             
      description: product.description,
      quantity: 1,
      price: product.prix,           
    });
    currentProductRef.value = ""; 
  } else {
    // Optionnel: afficher un message d'erreur si le produit n'est pas trouvé
    alert("Produit non trouvé. Veuillez vérifier la référence.");
  }
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

// Calcul du montant restant à payer
const reste = computed(() => {
  return total.value - invoice.value.montantVerse;
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

// Assigner automatiquement un numéro de facture au chargement
// et charger les données depuis les API
onMounted(async () => {
  invoice.value.number = generateInvoiceNumber();
  
  // Chargement des données depuis les API
  await Promise.all([fetchProducts(), fetchPartners()]);
});

const saveInvoice = async () => {
  const { success, error } = useNotification();

  try {
    // Vérifications initiales
    if (invoice.value.items.length === 0) {
      error("Veuillez ajouter au moins un article");
      return;
    }

    if (!invoice.value.recipientType) {
      error("Veuillez sélectionner un type de destinataire");
      return;
    }

    // Préparation des données de la facture
    const factureData = {
      type: invoice.value.recipientType,
      total: total.value,
      reste: reste.value,
      status: reste.value > 0 ? 'encours' : 'payé',
      created_at: new Date().toISOString(),
      boutique: 1, // À remplacer par l'ID réel de la boutique
      created_by: 1 // À remplacer par l'ID de l'utilisateur connecté
    };

    // 1. Enregistrement de la facture principale
    const { data: facture, error: factureError } = await useApi(
      'http://127.0.0.1:8000/api/factures/',
      {
        method: 'POST',
        body: factureData,
        server: false
      }
    );

    if (factureError.value || !facture.value?.id) {
      error("Erreur lors de la création de la facture");
      console.error("Détails:", factureError.value);
      return;
    }

    // 2. Enregistrement des commandes selon le type
    let endpoint = '';
    const commandes = invoice.value.items.map(item => {
      const product = products.value.find(p => p.reference === item.reference);
      return {
        quantite: item.quantity,
        prix_unitaire_fcfa: item.price,
        total: item.quantity * item.price,
        produit: product?.id || 0,
        facture: facture.value.id
      };
    });

    if (invoice.value.recipientType === 'client') {
      endpoint = 'http://127.0.0.1:8000/api/commandes-client/';
      
      // Création du client si nécessaire (à adapter selon votre API)
      const { data: client } = await useApi(endpoint, {
        method: 'POST',
        body: invoice.value.client,
        server: false
      });

      commandes.forEach(cmd => cmd.client = client.value?.id);
    } else {
      endpoint = 'http://127.0.0.1:8000/api/commandes-partenaire/';
      
      const selectedPartner = partners.value.find(
        p => `${p.prenom} ${p.nom}` === invoice.value.partenaire
      );

      if (!selectedPartner?.id) {
        error("Partenaire introuvable");
        return;
      }

      commandes.forEach(cmd => cmd.partenaire = selectedPartner.id);
    }

    // Envoi des commandes
    const { error: commandesError } = await useApi(endpoint, {
      method: 'POST',
      body: commandes,
      server: false
    });

    if (commandesError.value) {
      error("Erreur lors de l'enregistrement des articles");
      return;
    }

    // Succès
    success(`Facture ${invoice.value.number} enregistrée`);
    console.log("Facture créée:", facture.value);

    // Réinitialisation
    invoice.value = {
      number: generateInvoiceNumber(),
      date: new Date().toISOString().split("T")[0],
      recipientType: "",
      client: { nom: "", prenom: "", telephone: "" },
      partenaire: "",
      items: [],
      taxRate: 10,
      montantVerse: 0,
    };

  } catch (err) {
    error("Erreur inattendue");
    console.error("Erreur complète:", err);
  }
};
</script>

<template>
  <section class="mt-5 px-6">
    <h2 class="text-xl md:text-3xl font-bold text-blue-400">Factures</h2>
    <div
      class="mt-7 border mx-auto dark:border-gray-600 dark:shadow-gray-800 shadow-xl rounded-lg overflow-hidden"
    >
      <div class="px-6 py-4 sm:p-6">
        <div class="mb-6">
          <label
            for="recipientType"
            class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2"
            >Client ou Partenaire ? </label
          >
          <URadio v-model="invoice.recipientType" value="client" name="recipientType" label="Client" color="blue" class="mr-4" />
          <URadio v-model="invoice.recipientType" value="partenaire" name="recipientType" label="Partenaire" color="blue" />
        </div>

        <div
          class="w-full grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6 mb-6"
        >
          <!-- Informations facture -->
          <div class="sm:col-span-3">
            <label
              for="invoiceNumber"
              class="block text-sm font-medium text-gray-700 dark:text-gray-200"
              >Numéro de la Facture</label
            >
            <UInput
              id="invoiceNumber"
              color="blue"
              variant="outline"
              v-model="invoice.number"
              class="mt-1"
              placeholder="Généré automatiquement"
              readonly
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
              color="blue"
              variant="outline"
              v-model="invoice.date"
              class="mt-1"
              placeholder="Date de la facture"
              type="date"
            />
          </div>

          <!-- Champs client (affichés si type client est sélectionné) -->
          <template v-if="invoice.recipientType === 'client'">
            <div class="sm:col-span-2">
              <label
                for="clientNom"
                class="block text-sm font-medium text-gray-700 dark:text-gray-200"
                >Nom du Client</label
              >
              <UInput
                id="clientNom"
                color="blue"
                variant="outline"
                v-model="invoice.client.nom"
                class="mt-1"
                placeholder="Nom du client"
              />
            </div>
            <div class="sm:col-span-2">
              <label
                for="clientPrenom"
                class="block text-sm font-medium text-gray-700 dark:text-gray-200"
                >Prénom du Client</label
              >
              <UInput
                id="clientPrenom"
                color="blue"
                variant="outline"
                v-model="invoice.client.prenom"
                class="mt-1"
                placeholder="Prénom du client"
              />
            </div>
            <div class="sm:col-span-2">
              <label
                for="clientTelephone"
                class="block text-sm font-medium text-gray-700 dark:text-gray-200"
                >Téléphone du Client</label
              >
              <UInput
                id="clientTelephone"
                color="blue"
                variant="outline"
                v-model="invoice.client.telephone"
                class="mt-1"
                placeholder="Téléphone du client"
              />
            </div>
          </template>

          <!-- Champs partenaire (affichés si type partenaire est sélectionné) -->
          <div class="sm:col-span-6" v-if="invoice.recipientType === 'partenaire'">
            <label
              for="partenaireSelect"
              class="block text-sm font-medium text-gray-700 dark:text-gray-200"
              >Sélectionner un Partenaire</label
            >
            <USelect
              id="partenaireSelect"
              color="blue"
              variant="outline"
              v-model="invoice.partenaire"
              class="mt-1"
              placeholder="Choisir un partenaire"
              :options="partners.map(p => `${p.prenom} ${p.nom}`)"
            />
          </div>
        </div>

        <!-- Invoice Items -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-blue-400 mb-3">
            Articles de la Facture
          </h2>
          
          <!-- Ajout d'article par référence -->
          <div class="flex flex-wrap sm:flex-nowrap items-center space-y-2 sm:space-y-0 sm:space-x-4 mb-4">
            <UInput
              v-model="currentProductRef"
              color="blue"
              variant="outline"
              placeholder="Référence du produit"
              class="flex-grow w-full sm:w-auto"
            />
            <UButton
              @click="addItem"
              color="blue"
              variant="solid"
              icon="i-heroicons-plus"
              class="w-full flex items-center justify-center sm:w-auto"
            >
              Ajouter
            </UButton>
          </div>
          
          <!-- Liste des articles ajoutés -->
          <div class="overflow-x-auto">
            <table class="w-full text-sm text-left text-gray-700 dark:text-gray-300 mt-3">
              <thead class="text-xs uppercase bg-gray-100 dark:bg-gray-700">
                <tr>
                  <th class="px-4 py-2">Référence</th>
                  <th class="px-4 py-2">Nom</th>
                  <th class="px-4 py-2">Description</th>
                  <th class="px-4 py-2">Prix</th>
                  <th class="px-4 py-2">Quantité</th>
                  <th class="px-4 py-2">Total</th>
                  <th class="px-4 py-2">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in invoice.items" :key="index" class="border-b dark:border-gray-600">
                  <td class="px-4 py-2">{{ item.reference }}</td>
                  <td class="px-4 py-2">{{ item.name }}</td>
                  <td class="px-4 py-2">{{ item.description }}</td>
                  <td class="px-4 py-2">{{ formatCurrency(item.price) }}</td>
                  <td class="px-4 py-2 w-24">
                    <UInput
                      type="number"
                      color="blue"
                      variant="outline"
                      v-model="item.quantity"
                      min="1"
                      class="w-full"
                    />
                  </td>
                  <td class="px-4 py-2">{{ formatCurrency(item.quantity * item.price) }}</td>
                  <td class="px-4 py-2">
                    <UButton
                      icon="i-heroicons-trash"
                      @click="removeItem(index)"
                      color="red"
                      size="sm"
                    >
                    </UButton>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Montant versé et reste à payer -->
        <div class="mb-6">
          <div
            class="flex justify-between items-center py-2 border-t border-gray-200 dark:border-gray-600"
          >
            <span class="text-sm font-medium text-gray-500 dark:text-gray-300"
              >Total produits :</span
            >
            <span
              class="text-sm font-medium text-gray-900 dark:text-gray-100"
              >{{ totalItems }}</span
            >
          </div>
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
            class="flex justify-between items-center py-2 border-t border-gray-200 dark:border-gray-600"
          >
            <span class="text-base font-medium text-gray-900 dark:text-gray-100"
              >Total :</span
            >
            <span
              class="text-base font-medium text-gray-900 dark:text-gray-100"
              >{{ formatCurrency(total) }}</span
            >
          </div>
          
          <!-- Montant versé -->
          <div class="mt-4 grid grid-cols-1 gap-y-2 sm:grid-cols-2 gap-x-4">
            <div>
              <label
                for="montantVerse"
                class="block text-sm font-medium text-gray-700 dark:text-gray-200"
                >Montant versé</label
              >
              <UInput
                id="montantVerse"
                color="blue"
                variant="outline"
                v-model="invoice.montantVerse"
                type="number"
                min="0"
                :max="total"
                class="mt-1"
                placeholder="Montant versé par le client"
              />
            </div>
            <div>
              <label
                class="block text-sm font-medium text-gray-700 dark:text-gray-200"
                >Reste à payer</label
              >
              <div class="mt-3 text-lg font-bold" :class="reste > 0 ? 'text-red-500' : 'text-green-500'">
                {{ formatCurrency(reste) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-4">
          <UButton
            @click="saveInvoice"
            color="green"
            variant="solid"
            size="lg"
            icon="i-heroicons-document-check"
          >
            Enregistrer la Facture
          </UButton>
          <UButton 
            @click="printInvoice" 
            size="lg" 
            icon="i-heroicons-printer"
            color="blue"
            variant="solid"
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
      <h1 class="text-3xl font-bold mb-6 text-blue-400">Facture</h1>
      <div class="mb-6">
        <p><strong>Numéro de la Facture :</strong> {{ invoice.number }}</p>
        <p><strong>Date :</strong> {{ invoice.date }}</p>
        
        <div v-if="invoice.recipientType === 'client'">
          <p><strong>Client :</strong> {{ invoice.client.prenom }} {{ invoice.client.nom }}</p>
          <p><strong>Téléphone :</strong> {{ invoice.client.telephone }}</p>
        </div>
        
        <div v-if="invoice.recipientType === 'partenaire'">
          <p><strong>Partenaire :</strong> {{ invoice.partenaire }}</p>
        </div>
      </div>
      
      <table class="w-full mb-6 border-collapse border">
        <thead>
          <tr class="bg-blue-50">
            <th class="border p-2 text-left">Référence</th>
            <th class="border p-2 text-left">Description</th>
            <th class="border p-2 text-right">Prix</th>
            <th class="border p-2 text-right">Quantité</th>
            <th class="border p-2 text-right">Total</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in invoice.items" :key="item.id" class="border-b">
            <td class="border p-2">{{ item.reference }}</td>
            <td class="border p-2">{{ item.name }} - {{ item.description }}</td>
            <td class="border p-2 text-right">{{ formatCurrency(item.price) }}</td>
            <td class="border p-2 text-right">{{ item.quantity }}</td>
            <td class="border p-2 text-right">
              {{ formatCurrency(item.quantity * item.price) }}
            </td>
          </tr>
        </tbody>
      </table>
      
      <div class="mb-6 text-right">
        <p><strong>Total produits :</strong> {{ totalItems }}</p>
        <p><strong>Sous-total :</strong> {{ formatCurrency(subtotal) }}</p>
        <p>
          <strong>Taxe ({{ invoice.taxRate }}%):</strong>
          {{ formatCurrency(taxAmount) }}
        </p>
        <p class="text-lg font-bold text-blue-400"><strong>Total :</strong> {{ formatCurrency(total) }}</p>
      </div>
    </div>
  </section>
</template>