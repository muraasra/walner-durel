<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useNotification } from '../types/useNotification';
import { Body } from "#components";
import { boolean } from "zod";
import { useAuthStore } from '@/stores/auth'
// Corriger l'import de jsPDF
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

const auth = useAuthStore()
const { error, success } = useNotification();

interface InvoiceBody {
  total: number;
  quantite: number;
  prix_unitaire_fcfa: number;
  prix_vente_vendeur?: number;
  justification?: string;
  nom: string;
  prenom: string;
  telephone: string;
  produit_id: number;
  facture?: number;
}

interface InvoiceBodyPartners {
  quantite: number;
  prix_unitaire_fcfa: number;
  prix_vente_vendeur?: number;
  justification?: string;
  partenaire: number;
  produit_id: number;
  facture?: number;
}

interface InvoiceItem {
  id: number;
  reference: string;
  name: string;
  description: string;
  quantity: number;
  price: number;
  prix_unitaire_fcfa: number;
  prix_vente_vendeur?: number;
  justification?: string;
  prix_achat?: number;
  category?: string;
  ram?: string;
  disque_dur?: string;
  processeur?: string;
  generation?: string;
  carte_graphique?: string;
  systeme_exploitation?: string;
  priceError?: string | null; // Corriger le type
}

interface Invoice {
  number: string;
  date: string;
  recipientType: 'client' | 'partenaire' | '';
  client: {
    id: number;
    nom: string;
    prenom: string;
    telephone: string;
  };
  partenaire?: string;
  items: InvoiceItem[];
  montantVerse: number;
  taxAmount?: number;
}

// Interface correspondant à la structure de votre API
interface Product {
  id: number;
  reference: string;
  nom: string;
  description: string;
  prix: number;
  prix_achat?: number; // Prix d'achat optionnel
  category?: string;
  quantite?: number;
  actif?: boolean;
  // Champs spécifiques pour les ordinateurs
  ram?: string;
  disque_dur?: string;
  processeur?: string;
  generation?: string;
  carte_graphique?: string;
  systeme_exploitation?: string;
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

// Interfaces pour les réponses API
interface StockResponse {
  quantite: number;
  id: number;
}

interface FactureResponse {
  id: number;
}

interface User {
  id: number;
  username: string;
  email?: string;
  role?: string;
  boutique?: {
    id: number;
    nom: string;
  };
  nom?: string;
  prenom?: string;
}

declare module '@/stores/auth' {
  interface AuthStore {
    user: User | null;
  }
}

// Corriger la déclaration du module jsPDF
declare module 'jspdf' {
  interface jsPDF {
    autoTable: typeof autoTable;
    lastAutoTable: {
      finalY: number;
    };
  }
}

const user = ref<User | null>(null);

if (process.client) {
  const userData = localStorage.getItem('user');
  if (userData) {
    user.value = JSON.parse(userData);
  }
}

const userId = computed(() => user.value?.id);

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

    // Mappez les données de l'API vers Product
    products.value = Array.isArray(data.value)
      ? data.value.map(p => ({
        id : p.id,
        reference: p.reference,
        nom: p.nom,
        description: p.description,
        prix: p.prix,
        prix_achat: p.prix_achat,
        category: p.category,
        quantite: p.quantite,
        actif: p.actif,
        ram: p.ram,
        disque_dur: p.disque_dur,
        processeur: p.processeur,
        generation: p.generation,
        carte_graphique: p.carte_graphique,
        systeme_exploitation: p.systeme_exploitation
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
  number: "",
  date: new Date().toISOString().split('T')[0],
  recipientType: '',
  client: {
    id: 0,
    nom: "",
    prenom: "",
    telephone: ""
  },
  partenaire: "",
  items: [],
  montantVerse: 0,
});

const currentProductRef = ref("");
const invoicePreview = ref<HTMLElement | null>(null);

// État pour la recherche de produits
const searchQuery = ref("");
const showProductSearch = ref(false);

// Computed pour filtrer les produits selon la recherche
const filteredProducts = computed(() => {
  if (!searchQuery.value) return [];
  
  const query = searchQuery.value.toLowerCase().trim();
  return products.value.filter(product => 
    product.reference.toLowerCase().includes(query) ||
    product.nom.toLowerCase().includes(query)
  ).slice(0, 5); // Limite à 5 résultats
});

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

// Sélection d'un produit depuis la liste de recherche
const selectProduct = async (product: Product) => {
  try {
    // Vérifier le stock disponible
    const { data: stockData } = await useApi<StockResponse>(`http://127.0.0.1:8000/api/produits/${product.id}`, {
      method: 'GET',
      server: false
    });

    if (!stockData.value || !stockData.value.quantite || stockData.value.quantite < 1) {
      alert("Stock insuffisant pour ce produit");
      return;
    }

    invoice.value.items.push({
      id: product.id,
      reference: product.reference,
      name: product.nom,
      description: product.description,
      quantity: 1,
      price: product.prix,
      prix_unitaire_fcfa: product.prix,
      prix_vente_vendeur: product.prix,
      prix_achat: product.prix_achat,
      justification: "",
      category: product.category,
      ram: product.ram,
      disque_dur: product.disque_dur,
      processeur: product.processeur,
      generation: product.generation,
      carte_graphique: product.carte_graphique,
      systeme_exploitation: product.systeme_exploitation
    });
    
    searchQuery.value = "";
    showProductSearch.value = false;
  } catch (err) {
    console.error("Erreur lors de la vérification du stock:", err);
    alert("Erreur lors de la vérification du stock");
  }
};

const removeItem = (index: number) => {
  invoice.value.items.splice(index, 1);
};

const subtotal = computed(() => {
  return invoice.value.items.reduce(
    (sum, item) => sum + item.quantity * item.price, // Utiliser item.price au lieu de prix_vente_vendeur
    0
  );
});

// const taxAmount = computed(() => {
//   return subtotal.value * (invoice.value.taxRate / 100);
// });

const total = computed(() => {
  return subtotal.value;
});

// Calcul du montant restant à payer
const reste = computed(() => {
  return total.value - invoice.value.montantVerse;
});

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "XAF",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount).replace(/\s/g, ' ');
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

// Constantes pour la facture
const COMPANY_INFO = {
  name: "ETS WALNER TECH",
  description: "Vente des Ordinateurs, Équipements Électroniques\nTéléphone portable et Accessoires, Import - Export\nMaintenance Ordinateur ; Installation Électronique",
  address: "Situé au Centre Commercial PELICAN Btq 221",
  nui: "P100017639977 B",
  phones: ["656 89 47 73", "651 70 97 52"],
  notice: "Les Marchandises vendues ne sont ni reprises ni échangées",
  warranty: "Garantie Produit – Service Après-Vente\nCe produit est couvert par une garantie de 6 mois à compter de la date d'achat figurant sur cette facture.\nEn cas de dysfonctionnement non causé par une mauvaise utilisation, vous pouvez bénéficier d'un service après-vente en présentant cette facture.\n\n Cette garantie couvre uniquement les défauts de fabrication et ne s'applique pas aux dommages physiques ou à l'usure normale.\n\nPour toute demande de prise en charge, contactez notre service client."
};

// Fonction pour générer le PDF (corrigée)
const generatePDF = async () => {
  try {
    const doc = new jsPDF();
    
    // En-tête
    doc.setFontSize(20);
    doc.text('Facture', 105, 20, { align: 'center' });
    
    // Informations de la boutique
    doc.setFontSize(12);
    doc.text(`Boutique: ${user.value?.boutique?.nom || ''}`, 20, 40);
    doc.text(`Date: ${new Date().toLocaleDateString()}`, 20, 50);
    
    // Informations du client
    if (invoice.value.recipientType === 'client' && invoice.value.client) {
      doc.text(`Client: ${invoice.value.client.prenom} ${invoice.value.client.nom}`, 20, 60);
      doc.text(`Téléphone: ${invoice.value.client.telephone}`, 20, 70);
    } else if (invoice.value.recipientType === 'partenaire') {
      doc.text(`Partenaire: ${invoice.value.partenaire}`, 20, 60);
    }
    
    // Tableau des produits
    const tableData = invoice.value.items.map(item => [
      item.reference,
      item.name,
      `${formatCurrency(item.price)} FCFA`,
      item.quantity.toString(),
      `${formatCurrency(item.quantity * item.price)} FCFA`
    ]);
    
    // Corriger l'appel à autoTable
    (doc as any).autoTable({
      startY: 80,
      head: [['Référence', 'Nom', 'Prix unitaire', 'Quantité', 'Total']],
      body: tableData,
      theme: 'grid',
      styles: { fontSize: 10 },
      headStyles: { fillColor: [41, 128, 185] }
    });
    
    // Total
    const finalY = (doc as any).lastAutoTable.finalY || 150;
    doc.text(`Total: ${formatCurrency(total.value)} FCFA`, 20, finalY + 20);
    
    // Montant versé
    doc.text("Montant versé: ", 20, finalY + 40);
    doc.text(formatCurrency(invoice.value.montantVerse), 150, finalY + 40);
    
    // Reste à payer
    doc.text("Reste à payer: ", 20, finalY + 50);
    doc.text(formatCurrency(reste.value), 150, finalY + 50);
    
    // Sauvegarder le PDF
    doc.save('facture.pdf');
    success('Facture générée et téléchargée');
    return true;
  } catch (err) {
    console.error('Erreur lors de la génération du PDF:', err);
    error('Erreur lors de la génération du PDF');
    return false;
  }
};

// Fonction pour convertir un nombre en lettres
const numberToWords = (number: number): string => {
  // Cette fonction devrait être implémentée pour convertir les nombres en lettres
  // Pour l'instant, retourne une chaîne simple
  return number.toString();
};

// Fonction pour valider le prix de vente et mettre à jour les totaux
const validatePrice = (item: InvoiceItem) => {
  const prixAchat = item.prix_achat || 0;
  const prixVente = item.price;
  const margeMinimale = 5000; // 5000 FCFA de marge minimale
  
  if (prixVente < prixAchat + margeMinimale) {
    // Ne pas révéler le prix d'achat dans le message d'erreur
    item.priceError = `Le prix de vente doit être au moins ${formatCurrency(prixAchat + margeMinimale)} FCFA`;
    return false;
  } else {
    item.priceError = undefined;
    // Mettre à jour prix_vente_vendeur quand le prix est valide
    item.prix_vente_vendeur = item.price;
    return true;
  }
};

// Ajouter la fonction getPriceValidationClass manquante
const getPriceValidationClass = (item: InvoiceItem) => {
  if (item.priceError) {
    return 'border-red-500 bg-red-50';
  }
  return '';
};

// Modification de la fonction d'ajout d'article
const addItem = () => {
  const product = findProductByReference(currentProductRef.value);
  if (!product) {
    error("Produit non trouvé");
    return;
  }

  const existingItem = invoice.value.items.find(item => item.reference === product.reference);
  if (existingItem) {
    existingItem.quantity++;
  } else {
    invoice.value.items.push({
      id: product.id,
      reference: product.reference,
      name: product.nom,
      description: product.description,
      quantity: 1,
      price: product.prix,
      prix_unitaire_fcfa: product.prix,
      prix_vente_vendeur: product.prix,
      prix_achat: product.prix_achat,
      justification: "",
      category: product.category,
      ram: product.ram,
      disque_dur: product.disque_dur,
      processeur: product.processeur,
      generation: product.generation,
      carte_graphique: product.carte_graphique,
      systeme_exploitation: product.systeme_exploitation
    });
  }
  currentProductRef.value = "";
};

// Corriger la fonction submitInvoice
const submitInvoice = async () => {
  try {
    // Validation des prix
    for (const item of invoice.value.items) {
      if (!validatePrice(item)) {
        return;
      }
    }

    // Utiliser l'ID de l'utilisateur connecté pour created_by
    // const userId = auth.user?.id; 
    if (!userId) { // Vérifier si l'utilisateur est connecté
        error("Utilisateur non connecté.");
        return;
    }

    if (invoice.value.items.length === 0) {
      error("Veuillez ajouter au moins un article");
      return;
    }

    if (!invoice.value.recipientType) {
      error("Veuillez sélectionner un type de destinataire");
      return;
    }

    // Vérifier le stock pour tous les articles avant de procéder
    for (const item of invoice.value.items) {
      const { data: stockData } = await useApi<StockResponse>(`http://127.0.0.1:8000/api/produits/${item.id}`, {
        method: 'GET',
        server: false
      });

      if (!stockData.value || !stockData.value.quantite || stockData.value.quantite < item.quantity) {
        error(`Stock insuffisant pour ${item.name}: ${stockData.value?.quantite || 0} disponible(s), ${item.quantity} demandé(s)`);
        return;
      }
    }

    let nomFacture: string = "";
    if (invoice.value.recipientType == "client") {
      nomFacture = invoice.value.client?.nom + ' ' + invoice.value.client?.prenom;
    }
    if (invoice.value.recipientType == "partenaire") {
      nomFacture = invoice.value.partenaire || ""; // Ajouter une valeur par défaut
    }
    
    const factureData = {
      type: invoice.value.recipientType,
      total: total.value,
      reste: reste.value,
      status: reste.value > 0 ? 'encours' : 'payé',
      nom: nomFacture,
      numero: invoice.value.number,
      boutique: user.value?.boutique?.id || 1, // Corriger l'accès à boutique
      created_by: userId
    };

    const { data: facture, error: factureError } = await useApi<FactureResponse>(
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

    if (invoice.value.recipientType === 'client') {
      const endpoint = 'http://127.0.0.1:8000/api/commandes-client/';
      let isSuccess = true;

      for (const item of invoice.value.items) {
        // Créer la commande
        const invoiceBody: InvoiceBody = {
          total: item.quantity * item.price, // Utiliser item.price
          quantite: item.quantity,
          prix_unitaire_fcfa: item.price, // Utiliser item.price
          prix_vente_vendeur: item.price, // Utiliser item.price
          justification: item.justification,
          nom: invoice.value.client?.nom || "",
          prenom: invoice.value.client?.prenom || "",
          telephone: invoice.value.client?.telephone || "",
          produit_id: item.id,
          facture: facture.value?.id,
        };

        try {
          // Enregistrer la commande
          const { data: commandeData, error: commandeError } = await useApi(endpoint, {
            method: 'POST',
            body: JSON.stringify(invoiceBody),
            server: false
          });

          if (commandeError.value) {
            error(commandeError.value.message || "Erreur lors de l'enregistrement de la commande");
            isSuccess = false;
            break;
          }

          // Mettre à jour le stock
          const { data: stockData } = await useApi<StockResponse>(`http://127.0.0.1:8000/api/produits/${item.id}`, {
            method: 'GET',
            server: false
          });

          if (stockData.value && typeof stockData.value.quantite === 'number') {
            const nouveauStock = stockData.value.quantite - item.quantity;
            
            await useApi(`http://127.0.0.1:8000/api/produits/${item.id}/`, {
              method: 'PATCH',
              body: JSON.stringify({ quantite: nouveauStock }),
              server: false
            });
          }

        } catch (err) {
          console.error(`Erreur pour l'article ${item.id}:`, err);
          isSuccess = false;
          break;
        }
      }

    if (isSuccess) {
        // Générer le PDF
      const pdfGenerated = await generatePDF();
      if (pdfGenerated) {
          success(`Facture client ${invoice.value.number} enregistrée et téléchargée`);
      } else {
        error("Erreur lors de la génération du PDF");
      }
      
        // Réinitialiser le formulaire
      invoice.value = {
        number: generateInvoiceNumber(),
        date: new Date().toISOString().split("T")[0],
        recipientType: "",
        client: { id: 0, nom: "", prenom: "", telephone: "" },
        partenaire: "",
        items: [],
        montantVerse: 0,
      };
      }

    } else {
      // Logique pour les partenaires...
      const endpoint = 'http://127.0.0.1:8000/api/commandes-partenaire/';
      let isSuccess = true;

      const selectedPartner = partners.value.find(
        p => `${p.prenom} ${p.nom}` === invoice.value.partenaire
      );

      if (!selectedPartner?.id) {
        error("Partenaire introuvable");
        return;
      }

      for (const item of invoice.value.items) {
        const invoiceBodyPartners: InvoiceBodyPartners = {
          quantite: item.quantity,
          prix_unitaire_fcfa: item.price, // Utiliser item.price
          prix_vente_vendeur: item.price, // Utiliser item.price
          justification: item.justification,
          partenaire: selectedPartner.id,
          produit_id: item.id,
          facture: facture.value?.id,
        };

        try {
          const { data: commandeData, error: commandeError } = await useApi(endpoint, {
            method: 'POST',
            body: JSON.stringify(invoiceBodyPartners),
            server: false
          });

          if (commandeError.value) {
            error(commandeError.value.message || "Erreur lors de l'enregistrement de la commande");
            isSuccess = false;
            break;
          }

          // Mettre à jour le stock
          const { data: stockData } = await useApi<StockResponse>(`http://127.0.0.1:8000/api/produits/${item.id}`, {
            method: 'GET',
            server: false
          });

          if (stockData.value && typeof stockData.value.quantite === 'number') {
            const nouveauStock = stockData.value.quantite - item.quantity;
            
            await useApi(`http://127.0.0.1:8000/api/produits/${item.id}/`, {
              method: 'PATCH',
              body: JSON.stringify({ quantite: nouveauStock }),
              server: false
            });
          }

        } catch (err) {
          console.error(`Erreur pour l'article ${item.id}:`, err);
          isSuccess = false;
          break;
        }
      }

      if (isSuccess) {
        // Générer le PDF
        const pdfGenerated = await generatePDF();
        if (pdfGenerated) {
          success(`Facture partenaire ${invoice.value.number} enregistrée et téléchargée`);
        } else {
          error("Erreur lors de la génération du PDF");
        }

        // Réinitialiser le formulaire
        invoice.value = {
          number: generateInvoiceNumber(),
          date: new Date().toISOString().split("T")[0],
          recipientType: "",
          client: { id: 0, nom: "", prenom: "", telephone: "" },
          partenaire: "",
          items: [],
          montantVerse: 0,
        };
      }
    }

  } catch (err) {
    error("Erreur inattendue");
    console.error("Erreur complète:", err);
  }
};

// Computed pour le nombre total d'articles
const totalItems = computed(() => {
  return invoice.value.items.reduce((sum, item) => sum + item.quantity, 0);
});

// Utility function for delay
const delay = (ms: number) => new Promise(resolve => window.setTimeout(resolve, ms));
</script>

<template>
  <section class="mt-5 px-6">
    <h2 class="text-xl md:text-3xl font-bold text-blue-400">Factures</h2>
    <div class="mt-7 border mx-auto dark:border-gray-600 dark:shadow-gray-800 shadow-xl rounded-lg overflow-hidden">
      <div class="px-6 py-4 sm:p-6">
        <div class="mb-6">
          <label for="recipientType" class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">Client ou
            Partenaire ? </label>
          <URadio v-model="invoice.recipientType" value="client" name="recipientType" label="Client" color="blue"
            class="mr-4" />
          <URadio v-model="invoice.recipientType" value="partenaire" name="recipientType" label="Partenaire"
            color="blue" />
        </div>

        <div class="w-full grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6 mb-6">
          <!-- Informations facture -->
          <div class="sm:col-span-3">
            <label for="invoiceNumber" class="block text-sm font-medium text-gray-700 dark:text-gray-200">Numéro de la
              Facture</label>
            <UInput id="invoiceNumber" color="blue" variant="outline" v-model="invoice.number" class="mt-1"
              placeholder="Généré automatiquement" readonly />
          </div>
          <div class="sm:col-span-3">
            <label for="invoiceDate" class="block text-sm font-medium text-gray-700 dark:text-gray-200">Date de la
              Facture</label>
            <UInput id="invoiceDate" color="blue" variant="outline" v-model="invoice.date" class="mt-1"
              placeholder="Date de la facture" type="date" />
          </div>

          <!-- Champs client (affichés si type client est sélectionné) -->
          <template v-if="invoice.recipientType === 'client'">
            <div class="sm:col-span-2">
              <label for="clientNom" class="block text-sm font-medium text-gray-700 dark:text-gray-200">Nom du
                Client</label>
              <UInput id="clientNom" color="blue" variant="outline" v-model="invoice.client.nom" class="mt-1"
                placeholder="Nom du client" />
            </div>
            <div class="sm:col-span-2">
              <label for="clientPrenom" class="block text-sm font-medium text-gray-700 dark:text-gray-200">Prénom du
                Client</label>
              <UInput id="clientPrenom" color="blue" variant="outline" v-model="invoice.client.prenom" class="mt-1"
                placeholder="Prénom du client" />
            </div>
            <div class="sm:col-span-2">
              <label for="clientTelephone" class="block text-sm font-medium text-gray-700 dark:text-gray-200">Téléphone
                du Client</label>
              <UInput id="clientTelephone" color="blue" variant="outline" v-model="invoice.client.telephone"
                class="mt-1" placeholder="Téléphone du client" />
            </div>
          </template>

          <!-- Champs partenaire (affichés si type partenaire est sélectionné) -->
          <div class="sm:col-span-6" v-if="invoice.recipientType === 'partenaire'">
            <label for="partenaireSelect"
              class="block text-sm font-medium text-gray-700 dark:text-gray-200">Sélectionner un
              Partenaire</label>
            <USelect id="partenaireSelect" color="blue" variant="outline" v-model="invoice.partenaire" class="mt-1"
              placeholder="Choisir un partenaire" :options="partners.map(p => `${p.prenom} ${p.nom}`)" />
          </div>
        </div>

        <!-- Invoice Items -->
    <div class="mb-6">
      <h2 class="text-xl font-semibold text-blue-400 mb-3">
        Articles de la Facture
      </h2>

      <!-- Recherche de produit avec suggestions -->
          <div class="relative mb-4">
        <UInput 
          v-model="searchQuery"
          color="blue"
          variant="outline"
          placeholder="Rechercher un produit par référence ou nom"
          class="w-full"
          @focus="showProductSearch = true"
              @blur="async () => { await delay(200); showProductSearch = false }"
        />
        
        <!-- Liste des suggestions -->
        <div v-if="showProductSearch && filteredProducts.length > 0" 
             class="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          <div v-for="product in filteredProducts" 
               :key="product.id"
               @click="selectProduct(product)"
                   class="p-3 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b dark:border-gray-700">
                <div class="flex justify-between items-center">
                  <div>
                    <div class="font-medium text-gray-900 dark:text-gray-100">{{ product.nom }}</div>
                    <div class="text-sm text-gray-600 dark:text-gray-400">Réf: {{ product.reference }}</div>
                  </div>
                  <div class="text-blue-500 font-medium">{{ formatCurrency(product.prix) }}</div>
                </div>
                <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Stock disponible: {{ product.quantite || 0 }}
                </div>
              </div>
            </div>
          </div>

          <!-- Liste des articles ajoutés -->
          <div class="overflow-x-auto">
            <table class="w-full text-sm text-left text-gray-700 dark:text-gray-300 mt-3">
              <thead class="text-xs uppercase bg-gray-100 dark:bg-gray-700">
                <tr>
                  <th class="px-4 py-2">Référence</th>
                  <th class="px-4 py-2">Nom</th>
                  <th class="px-4 py-2">Description</th>
                  <th class="px-4 py-2">Prix de vente</th>
                  <th class="px-4 py-2">Justification</th>
                  <th class="px-4 py-2">Quantité</th>
                  <th class="px-4 py-2">Total</th>
                  <th class="px-4 py-2">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in invoice.items" :key="index" class="border-b dark:border-gray-600">
                  <td class="px-4 py-2">{{ item.reference }}</td>
                  <td class="px-4 py-2">
                    {{ item.name }}
                    <div v-if="item.category?.toLowerCase() === 'ordinateur'" class="text-sm text-gray-600 mt-1">
                      <div v-if="item.ram">RAM: {{ item.ram }}</div>
                      <div v-if="item.disque_dur">Disque dur: {{ item.disque_dur }}</div>
                      <div v-if="item.processeur">Processeur: {{ item.processeur }}</div>
                      <div v-if="item.generation">Génération: {{ item.generation }}</div>
                      <div v-if="item.carte_graphique">Carte graphique: {{ item.carte_graphique }}</div>
                      <div v-if="item.systeme_exploitation">OS: {{ item.systeme_exploitation }}</div>
                    </div>
                  </td>
                  <td class="px-4 py-2">{{ item.description }}</td>
                  <td class="px-4 py-2 w-32">
                    <UInput 
                      type="number" 
                      color="blue" 
                      variant="outline" 
                      v-model="item.price" 
                      min="0"
                      class="w-full"
                      :class="getPriceValidationClass(item)"
                      @input="validatePrice(item)"
                    />
                    <div v-if="item.priceError" class="text-xs text-red-500 mt-1">
                      {{ item.priceError }}
                    </div>
                  </td>
                  <td class="px-4 py-2">
                    <UInput
                      v-model="item.justification"
                      placeholder="Justification du prix"
                      class="w-full"
                      :disabled="!item.price || item.price === item.prix_vente_vendeur"
                    />
                  </td>
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
                  <td class="px-4 py-2">
                    {{ formatCurrency(item.quantity * item.price) }}
                  </td>
                  <td class="px-4 py-2">
                    <UButton 
                      icon="i-heroicons-trash" 
                      @click="removeItem(index)" 
                      color="red" 
                      size="sm"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Montant versé et reste à payer -->
        <div class="mb-6">
          <div class="flex justify-between items-center py-2 border-t border-gray-200 dark:border-gray-600">
            <span class="text-sm font-medium text-gray-500 dark:text-gray-300">Total produits :</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ totalItems }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-t border-gray-200 dark:border-gray-600">
            <span class="text-sm font-medium text-gray-500 dark:text-gray-300">Sous-total :</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(subtotal) }}</span>
          </div>
           
          <div class="flex justify-between items-center py-2 border-t border-gray-200 dark:border-gray-600">
            <span class="text-base font-medium text-gray-900 dark:text-gray-100">Total :</span>
            <span class="text-base font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(total) }}</span>
          </div>

          <!-- Montant versé -->
          <div class="mt-4 grid grid-cols-1 gap-y-2 sm:grid-cols-2 gap-x-4">
            <div>
              <label for="montantVerse" class="block text-sm font-medium text-gray-700 dark:text-gray-200">Montant
                versé</label>
              <UInput id="montantVerse" color="blue" variant="outline" v-model="invoice.montantVerse" type="number"
                min="0" :max="total" class="mt-1" placeholder="Montant versé par le client" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Reste à payer</label>
              <div class="mt-3 text-lg font-bold" :class="reste > 0 ? 'text-red-500' : 'text-green-500'">
                {{ formatCurrency(reste) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-4">
          <UButton @click="submitInvoice" color="green" variant="solid" size="lg" icon="i-heroicons-document-check">
            Enregistrer la Facture
          </UButton>
          <UButton @click="printInvoice" size="lg" icon="i-heroicons-printer" color="blue" variant="solid">
            Imprimer la Facture
          </UButton>
        </div>
      </div>
    </div>

    <!-- Invoice Preview (for printing) -->
    <div ref="invoicePreview" class="hidden bg-white p-8 max-w-4xl mx-auto mt-8">
      <h1 class="text-3xl font-bold mb-6 text-blue-400">Facture</h1>
      <div class="mb-6">
        <p><strong>Numéro de la Facture :</strong> {{ invoice.number }}</p>
        <p><strong>Date :</strong> {{ invoice.date }}</p>

        <div v-if="invoice.recipientType === 'client' && invoice.client">
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
            <td class="border p-2">
              {{ item.name }} - {{ item.description }}
              <div v-if="item.category?.toLowerCase() === 'ordinateur'" class="text-sm text-gray-600 mt-1">
                <div v-if="item.ram">RAM: {{ item.ram }}</div>
                <div v-if="item.disque_dur">Disque dur: {{ item.disque_dur }}</div>
                <div v-if="item.processeur">Processeur: {{ item.processeur }}</div>
                <div v-if="item.generation">Génération: {{ item.generation }}</div>
                <div v-if="item.carte_graphique">Carte graphique: {{ item.carte_graphique }}</div>
                <div v-if="item.systeme_exploitation">OS: {{ item.systeme_exploitation }}</div>
              </div>
            </td>
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
        <p class="text-lg font-bold text-blue-400"><strong>Total :</strong> {{ formatCurrency(total) }}</p>
      </div>
    </div>
  </section>
</template>