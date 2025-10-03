<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useNotification } from '../types/useNotification';
import { Body } from "#components";
import { boolean } from "zod";
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const { addToast, success } = useNotification();
const error = (msg: string) => addToast(msg, 'error');

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
  priceError?: string | null;
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

  // 🟦 AJOUT: garantie en mois (déjà existant) + clauses personnalisables
  garantie: number;
  contrat_confidentialite: boolean;
  taxAmount?: number;
}

// ---- API types ----
interface Product {
  id: number;
  reference: string;
  nom: string;
  description: string;
  prix: number;
  prix_achat?: number;
  category?: string;
  quantite?: number;
  actif?: boolean;
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

const user = ref<User | null>(null);
if (process.client) {
  const userData = localStorage.getItem('user');
  if (userData) user.value = JSON.parse(userData);
}
const userId = computed<number | null>(() => user.value?.id ?? null);

// ---- Produits & Partenaires ----
const products = ref<Product[]>([]);
const fetchProducts = async () => {
  try {
    const { data, error } = await useApi('http://127.0.0.1:8000/api/produits/', { method: 'GET', server: false });
    if (error.value) return console.error("Erreur produits:", error.value);
    products.value = Array.isArray(data.value)
      ? data.value.map(p => ({
        id: p.id, reference: p.reference, nom: p.nom, description: p.description,
        prix: p.prix, prix_achat: p.prix_achat, category: p.category, quantite: p.quantite, actif: p.actif,
        ram: p.ram, disque_dur: p.disque_dur, processeur: p.processeur, generation: p.generation,
        carte_graphique: p.carte_graphique, systeme_exploitation: p.systeme_exploitation
      }))
      : [];
  } catch (err) { console.error("Erreur inattendue produits:", err); }
};

const partners = ref<Partner[]>([]);
const fetchPartners = async () => {
  try {
    const { data, error } = await useApi('http://127.0.0.1:8000/api/partenaires/', { method: 'GET', server: false });
    if (error.value) return console.error("Erreur partenaires:", error.value);
    partners.value = Array.isArray(data.value) ? data.value : [];
  } catch (err) { console.error("Erreur inattendue partenaires:", err); }
};

// ---- Facture ----
const invoice = ref<Invoice>({
  number: "",
  date: new Date().toISOString().split('T')[0],
  recipientType: '',
  client: { id: 0, nom: "", prenom: "", telephone: "" },
  partenaire: "",
  items: [],
  montantVerse: 0,

  // 🟦 AJOUT: valeur par défaut modifiable
  garantie: 6,
  contrat_confidentialite: false,
});

const currentProductRef = ref("");
const invoicePreview = ref<HTMLElement | null>(null);

// 🟦 AJOUT: texte de garantie personnalisable visible dans formulaire + PDF
const warrantyClauses = ref<string>(
  "Garantie Produit – Service Après-Vente\n" +
  "Ce produit est couvert par une garantie à compter de la date d'achat de cette facture.\n" +
  "En cas de dysfonctionnement non causé par une mauvaise utilisation, vous pouvez bénéficier d'un SAV en présentant cette facture.\n\n" +
  "Cette garantie couvre uniquement les défauts de fabrication et ne s'applique pas aux dommages physiques ou à l'usure normale.\n\n" +
  "Pour toute demande de prise en charge, contactez notre service client."
);

// 🟦 AJOUT: helpers de date pour période de garantie
const formatFR = (d: Date) => d.toLocaleDateString('fr-FR');
function addMonths(dateISO: string, months: number): string {
  const d = new Date(dateISO);
  const m = d.getMonth() + months;
  const end = new Date(d.getFullYear(), m, d.getDate());
  return end.toISOString().split('T')[0];
}
const warrantyStart = computed(() => invoice.value.date);
const warrantyEnd = computed(() => addMonths(invoice.value.date, Number(invoice.value.garantie || 0)));

// ---- Recherche Produits ----
const searchQuery = ref("");
const showProductSearch = ref(false);
const filteredProducts = computed(() => {
  if (!searchQuery.value) return [];
  const q = searchQuery.value.toLowerCase().trim();
  return products.value
    .filter(p => p.reference.toLowerCase().includes(q) || p.nom.toLowerCase().includes(q))
    .slice(0, 5);
});

function generateInvoiceNumber(): string {
  const prefix = "FACT";
  const d = new Date(); const y = d.getFullYear().toString().slice(-2);
  const m = (d.getMonth() + 1).toString().padStart(2, "0");
  const rnd = Math.floor(Math.random() * 10000).toString().padStart(4, "0");
  return `${prefix}-${y}${m}-${rnd}`;
}
const findProductByReference = (reference: string) =>
  products.value.find(p => p.reference === reference);

// ---- Ajout produit depuis la recherche ----
const selectProduct = async (product: Product) => {
  try {
    const { data: stockData } = await useApi<StockResponse>(`http://127.0.0.1:8000/api/produits/${product.id}`, { method: 'GET', server: false });
    if (!stockData.value || !stockData.value.quantite || stockData.value.quantite < 1) {
      alert("Stock insuffisant pour ce produit"); return;
    }
    invoice.value.items.push({
      id: product.id, reference: product.reference, name: product.nom, description: product.description,
      quantity: 1, price: product.prix, prix_unitaire_fcfa: product.prix, prix_vente_vendeur: product.prix,
      prix_achat: product.prix_achat, justification: "", category: product.category,
      ram: product.ram, disque_dur: product.disque_dur, processeur: product.processeur,
      generation: product.generation, carte_graphique: product.carte_graphique, systeme_exploitation: product.systeme_exploitation
    });
    searchQuery.value = ""; showProductSearch.value = false;
  } catch (err) {
    console.error("Erreur vérif stock:", err); alert("Erreur lors de la vérification du stock");
  }
};

const removeItem = (index: number) => invoice.value.items.splice(index, 1);

const subtotal = computed(() =>
  invoice.value.items.reduce((s, it) => s + it.quantity * it.price, 0)
);
const total = computed(() => subtotal.value);
const reste = computed(() => total.value - invoice.value.montantVerse);

const formatCurrency = (amount: number) =>
  new Intl.NumberFormat("fr-FR", { style: "currency", currency: "XAF", minimumFractionDigits: 0, maximumFractionDigits: 0 })
    .format(amount).replace(/\s/g, ' ');

const printInvoice = () => {
  const html = invoicePreview.value?.innerHTML;
  const orig = document.body.innerHTML;
  document.body.innerHTML = html || ""; window.print(); document.body.innerHTML = orig;
};

onMounted(async () => {
  invoice.value.number = generateInvoiceNumber();
  await Promise.all([fetchProducts(), fetchPartners()]);
});

// ---- PDF ----
const COMPANY_INFO = {
  name: "ETS WALNER TECH",
  address: "Situé au Centre Commercial PELICAN Btq 221",
  nui: "P100017639977 B",
  phones: ["656 89 47 73", "651 70 97 52"],
  notice: "Les Marchandises vendues ne sont ni reprises ni échangées",
};

// 🟦 AJOUT: PDF plus stylé + période & clauses de garantie


// --- remplace entièrement generatePDF par ceci ---
const generatePDF = async () => {
  try {
    if (!process.client) return false

    const { jsPDF } = await import('jspdf')
    const autoTable = (await import('jspdf-autotable')).default

    const doc = new jsPDF('p', 'mm', 'a4')

    // Marges et curseur Y
    const M = { t: 18, r: 15, b: 18, l: 15 }
    let y = M.t

    // En-tête (barre bleue)
    doc.setFillColor(30, 100, 200)
    doc.rect(0, 0, 210, 28, 'F')

    doc.setTextColor(255, 255, 255)
    doc.setFontSize(16)
    doc.text('ETS WALNER TECH', M.l, 12)
    doc.setFontSize(10)
    doc.text('Situé au Centre Commercial PELICAN Btq 221', M.l, 18)
    doc.text('NUI: P100017639977 B   Tél.: 656 89 47 73 / 651 70 97 52', M.l, 24)

    doc.setTextColor(255, 255, 255)
    doc.text(`Date : ${new Date().toLocaleDateString('fr-FR')}`, 210 - M.r, 12, { align: 'right' })

    // Infos destinataire
    doc.setTextColor(0, 0, 0)
    y = 34
    doc.setFontSize(12)
    if (invoice.value.recipientType === 'client') {
      doc.text(`Client : ${invoice.value.client.prenom} ${invoice.value.client.nom}`.trim(), M.l, y)
      y += 6
      doc.text(`Téléphone : ${invoice.value.client.telephone || ''}`, M.l, y)
    } else if (invoice.value.recipientType === 'partenaire') {
      doc.text(`Partenaire : ${invoice.value.partenaire || ''}`, M.l, y)
    }
    y += 10

    // Tableau produits
    const rows = invoice.value.items.map(i => [
      i.reference,
      i.name,
      formatCurrency(i.price),          // ❗️PAS de " FCFA" ajouté
      String(i.quantity),
      formatCurrency(i.quantity * i.price),
    ])

    autoTable(doc, {
      startY: y,
      margin: { left: M.l, right: M.r },
      head: [['Référence', 'Désignation', 'Prix unitaire', 'Quantité', 'Total']],
      body: rows,
      theme: 'grid',
      styles: { fontSize: 11, cellPadding: 3 },
      headStyles: { fillColor: [30, 100, 200], halign: 'center', valign: 'middle', textColor: 255 },
      columnStyles: { 2: { halign: 'right' }, 3: { halign: 'center' }, 4: { halign: 'right' } },
      didDrawPage: (data) => { /* utile si plusieurs pages */ }
    })
    y = (doc as any).lastAutoTable.finalY + 8

    // Totaux (bloc aligné à droite, pas de chevauchement)
    doc.setFontSize(12)
    doc.setFont('helvetica', 'bold')
    doc.text('TOTAL', 130, y)
    doc.text(formatCurrency(Number(total.value)), 195, y, { align: 'right' })
    y += 8

    doc.setFont('helvetica', 'normal')
    doc.text('Montant versé :', 130, y)
    doc.text(formatCurrency(Number(invoice.value.montantVerse)), 195, y, { align: 'right' })
    y += 8

    doc.text('Reste à payer :', 130, y)
    doc.text(formatCurrency(Number(total.value - invoice.value.montantVerse)), 195, y, { align: 'right' })
    y += 14

    // Mention “non repris/échangé”
    doc.setFontSize(10)
    doc.setTextColor(90)
    doc.text('Les Marchandises vendues ne sont ni reprises ni échangées', M.l, y)
    y += 8

    // Bloc Garantie (avec encadré + maxWidth pour éviter que le texte passe sous autre chose)
    const warranty = [
      `Garantie: ${invoice.value.garantie} mois (du ${new Date().toLocaleDateString('fr-FR')} au ${
        new Date(new Date().setMonth(new Date().getMonth() + Number(invoice.value.garantie || 0)))
          .toLocaleDateString('fr-FR')
      })`,
      '',
      'Garantie Produit – Service Après-Vente',
      "Ce produit est couvert par une garantie à compter de la date d'achat de cette facture.",
      "En cas de dysfonctionnement non causé par une mauvaise utilisation, vous pouvez bénéficier d'un SAV en présentant cette facture.",
      '',
      "Cette garantie couvre uniquement les défauts de fabrication et ne s'applique pas aux dommages physiques ou à l'usure normale.",
      '',
      'Pour toute demande de prise en charge, contactez notre service client.'
    ].join('\n')

    // Encadré
    doc.setDrawColor(220)
    doc.setFillColor(245, 245, 245)
    const boxX = M.l, boxW = 210 - M.l - M.r
    const lines = doc.splitTextToSize(warranty, boxW - 10)
    const boxH = lines.length * 5 + 10
    doc.roundedRect(boxX, y, boxW, boxH, 3, 3, 'FD')
    doc.setTextColor(40)
    doc.text(lines, boxX + 5, y + 7)
    y += boxH + 16

    // Signatures
    doc.setTextColor(0)
    doc.text('Signature Client', M.l, y)
    doc.text('Signature Vendeur', 210 - M.r, y, { align: 'right' })

    doc.save('facture.pdf')
    success('Facture générée et téléchargée')
    return true
  } catch (e) {
    console.error(e)
    error('Erreur lors de la génération du PDF')
    return false
  }
};


// ---- validation prix ----
const validatePrice = (item: InvoiceItem) => {
  const achat = item.prix_achat || 0;
  const vente = item.price;
  const margeMin = 5000;
  if (vente < achat + margeMin) {
    item.priceError = `Le prix de vente doit être au moins ${formatCurrency(achat + margeMin)} FCFA`;
    return false;
  }
  item.priceError = undefined;
  item.prix_vente_vendeur = item.price;
  return true;
};
const getPriceValidationClass = (item: InvoiceItem) => item.priceError ? 'border-red-500 bg-red-50' : '';

// ---- ajout produit par ref ----
const addItem = () => {
  const product = findProductByReference(currentProductRef.value);
  if (!product) return error("Produit non trouvé");
  const exist = invoice.value.items.find(i => i.reference === product.reference);
  if (exist) exist.quantity++;
  else {
    invoice.value.items.push({
      id: product.id, reference: product.reference, name: product.nom, description: product.description,
      quantity: 1, price: product.prix, prix_unitaire_fcfa: product.prix, prix_vente_vendeur: product.prix,
      prix_achat: product.prix_achat, justification: "", category: product.category,
      ram: product.ram, disque_dur: product.disque_dur, processeur: product.processeur,
      generation: product.generation, carte_graphique: product.carte_graphique, systeme_exploitation: product.systeme_exploitation
    });
  }
  currentProductRef.value = "";
};

// ---- submit ----
const submitInvoice = async () => {
  try {
    for (const item of invoice.value.items) { if (!validatePrice(item)) return; }
    if (!userId.value) return error("Utilisateur non connecté.");
    if (invoice.value.items.length === 0) return error("Veuillez ajouter au moins un article");
    if (!invoice.value.recipientType) return error("Veuillez sélectionner un type de destinataire");

    // Vérifier stocks
    for (const it of invoice.value.items) {
      const { data: stockData } = await useApi<StockResponse>(`http://127.0.0.1:8000/api/produits/${it.id}`, { method: 'GET', server: false });
      if (!stockData.value || !stockData.value.quantite || stockData.value.quantite < it.quantity) {
        return error(`Stock insuffisant pour ${it.name}: ${stockData.value?.quantite || 0} dispo(s), ${it.quantity} demandé(s)`);
      }
    }

    let nomFacture = "";
    if (invoice.value.recipientType == "client") nomFacture = `${invoice.value.client.nom} ${invoice.value.client.prenom}`.trim();
    if (invoice.value.recipientType == "partenaire") nomFacture = invoice.value.partenaire || "";

    const factureData = {
      type: invoice.value.recipientType,
      total: Number(total.value),
      reste: Number(reste.value),
      status: reste.value > 0 ? 'encours' : 'payé',
      nom: nomFacture,
      numero: invoice.value.number,
      boutique: user.value?.boutique?.id || 1,
      created_by: userId.value,
      garantie: Number(invoice.value.garantie) || 0,           // 🟦 reste envoyé au backend
      contrat_confidentialite: !!invoice.value.contrat_confidentialite
      // NB: clauses de garantie → uniquement dans le PDF (pas de champ backend)
    };

    const { data: facture, error: factureError } = await useApi<FactureResponse>('http://127.0.0.1:8000/api/factures/', {
      method: 'POST', body: factureData, server: false
    });
    if (factureError.value || !facture.value?.id) {
      console.error("Détails:", factureError.value);
      return error("Erreur lors de la création de la facture");
    }

    if (invoice.value.recipientType === 'client') {
      const endpoint = 'http://127.0.0.1:8000/api/commandes-client/';
      let ok = true;
      for (const it of invoice.value.items) {
        const body: InvoiceBody = {
          total: it.quantity * it.price,
          quantite: it.quantity,
          prix_unitaire_fcfa: it.price,
          prix_vente_vendeur: it.price,
          justification: it.justification,
          nom: invoice.value.client.nom || "",
          prenom: invoice.value.client.prenom || "",
          telephone: invoice.value.client.telephone || "",
          produit_id: it.id,
          facture: facture.value.id,
        };
        const { error: e } = await useApi(endpoint, { method: 'POST', body, server: false });
        if (e.value) { error(e.value.message || "Erreur commande"); ok = false; break; }

        // Update stock
        const { data: stock } = await useApi<StockResponse>(`http://127.0.0.1:8000/api/produits/${it.id}/`, { method: 'GET', server: false });
        if (stock.value && typeof stock.value.quantite === 'number') {
          await useApi(`http://127.0.0.1:8000/api/produits/${it.id}/`, { method: 'PATCH', body: { quantite: stock.value.quantite - it.quantity }, server: false });
        }
      }
      if (ok) {
        const pdfGenerated = await generatePDF();
        if (pdfGenerated) success(`Facture client ${invoice.value.number} enregistrée et téléchargée`);
        else error("Erreur lors de la génération du PDF");
        invoice.value = {
          number: generateInvoiceNumber(),
          date: new Date().toISOString().split("T")[0],
          recipientType: "", client: { id: 0, nom: "", prenom: "", telephone: "" },
          partenaire: "", items: [], montantVerse: 0, garantie: 6, contrat_confidentialite: false,
        };
      }
    } else {
      // partenaire
      const endpoint = 'http://127.0.0.1:8000/api/commandes-partenaire/';
      let ok = true;
      const selected = partners.value.find(p => `${p.prenom} ${p.nom}` === invoice.value.partenaire);
      if (!selected?.id) return error("Partenaire introuvable");

      for (const it of invoice.value.items) {
        const body: InvoiceBodyPartners = {
          quantite: it.quantity, prix_unitaire_fcfa: it.price, prix_vente_vendeur: it.price,
          justification: it.justification, partenaire: selected.id, produit_id: it.id, facture: facture.value.id,
        };
        const { error: e } = await useApi(endpoint, { method: 'POST', body, server: false });
        if (e.value) { error(e.value.message || "Erreur commande partenaire"); ok = false; break; }

        const { data: stock } = await useApi<StockResponse>(`http://127.0.0.1:8000/api/produits/${it.id}`, { method: 'GET', server: false });
        if (stock.value && typeof stock.value.quantite === 'number') {
          await useApi(`http://127.0.0.1:8000/api/produits/${it.id}/`, { method: 'PATCH', body: { quantite: stock.value.quantite - it.quantity }, server: false });
        }
      }
      if (ok) {
        const pdfGenerated = await generatePDF();
        if (pdfGenerated) success(`Facture partenaire ${invoice.value.number} enregistrée et téléchargée`);
        else error("Erreur lors de la génération du PDF");
        invoice.value = {
          number: generateInvoiceNumber(),
          date: new Date().toISOString().split("T")[0],
          recipientType: "", client: { id: 0, nom: "", prenom: "", telephone: "" },
          partenaire: "", items: [], montantVerse: 0, garantie: 6, contrat_confidentialite: false,
        };
      }
    }
  } catch (err) {
    error("Erreur inattendue");
    console.error("Erreur complète:", err);
  }
};

const totalItems = computed(() =>
  invoice.value.items.reduce((sum, item) => sum + item.quantity, 0)
);

const delay = (ms: number) => new Promise(resolve => window.setTimeout(resolve, ms));
</script>

<template>
  <section class="mt-5 px-6">
    <h2 class="text-xl md:text-3xl font-bold text-blue-400">Factures</h2>
    <div class="mt-7 border mx-auto dark:border-gray-600 dark:shadow-gray-800 shadow-xl rounded-lg overflow-hidden">
      <div class="px-6 py-4 sm:p-6">
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">Client ou Partenaire ?</label>
          <URadio v-model="invoice.recipientType" value="client" name="recipientType" label="Client" color="blue" class="mr-4" />
          <URadio v-model="invoice.recipientType" value="partenaire" name="recipientType" label="Partenaire" color="blue" />
        </div>

        <div class="w-full grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6 mb-6">
          <div class="sm:col-span-3">
            <label for="invoiceNumber" class="block text-sm font-medium text-gray-700 dark:text-gray-200">Numéro de la Facture</label>
            <UInput id="invoiceNumber" color="blue" variant="outline" v-model="invoice.number" class="mt-1" placeholder="Généré automatiquement" readonly />
          </div>
          <div class="sm:col-span-3">
            <label for="invoiceDate" class="block text-sm font-medium text-gray-700 dark:text-gray-200">Date de la Facture</label>
            <UInput id="invoiceDate" color="blue" variant="outline" v-model="invoice.date" class="mt-1" type="date" />
          </div>

          <template v-if="invoice.recipientType === 'client'">
            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Nom</label>
              <UInput color="blue" variant="outline" v-model="invoice.client.nom" class="mt-1" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Prénom</label>
              <UInput color="blue" variant="outline" v-model="invoice.client.prenom" class="mt-1" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Téléphone</label>
              <UInput color="blue" variant="outline" v-model="invoice.client.telephone" class="mt-1" />
            </div>
          </template>

          <div class="sm:col-span-6" v-if="invoice.recipientType === 'partenaire'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Sélectionner un Partenaire</label>
            <USelect color="blue" variant="outline" v-model="invoice.partenaire" class="mt-1"
                     placeholder="Choisir un partenaire" :options="partners.map(p => `${p.prenom} ${p.nom}`)" />
          </div>

          <!-- 🟦 AJOUT: Formulaire garantie -->
          <div class="sm:col-span-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Garantie (mois)</label>
            <UInput type="number" min="0" max="36" color="blue" variant="outline" v-model.number="invoice.garantie" class="mt-1" />
            <p class="text-xs text-gray-500 mt-1">
              Période : {{ new Date(invoice.date).toLocaleDateString('fr-FR') }} → {{ new Date(warrantyEnd).toLocaleDateString('fr-FR') }}
            </p>
          </div>
          <div class="sm:col-span-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Clauses de garantie (apparaîtront sur le PDF)</label>
            <UTextarea :rows="4" color="blue" variant="outline" v-model="warrantyClauses" class="mt-1" />
          </div>
        </div>

        <!-- Articles -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-blue-400 mb-3">Articles de la Facture</h2>
          <div class="relative mb-4">
            <UInput v-model="searchQuery" color="blue" variant="outline"
                    placeholder="Rechercher un produit par référence ou nom"
                    class="w-full" @focus="showProductSearch = true"
                    @blur="async () => { await delay(200); showProductSearch = false }" />
            <div v-if="showProductSearch && filteredProducts.length"
                 class="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              <div v-for="product in filteredProducts" :key="product.id"
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
                    <UInput type="number" color="blue" variant="outline" v-model="item.price" min="0"
                            class="w-full" :class="getPriceValidationClass(item)" @input="validatePrice(item)" />
                    <div v-if="item.priceError" class="text-xs text-red-500 mt-1">{{ item.priceError }}</div>
                  </td>
                  <td class="px-4 py-2">
                    <UInput v-model="item.justification" placeholder="Justification du prix" class="w-full"
                            :disabled="!item.price || item.price === item.prix_vente_vendeur" />
                  </td>
                  <td class="px-4 py-2 w-24">
                    <UInput type="number" color="blue" variant="outline" v-model="item.quantity" min="1" class="w-full" />
                  </td>
                  <td class="px-4 py-2">{{ formatCurrency(item.quantity * item.price) }}</td>
                  <td class="px-4 py-2">
                    <UButton icon="i-heroicons-trash" @click="removeItem(index)" color="red" size="sm" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Totaux -->
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

          <div class="mt-4 grid grid-cols-1 gap-y-2 sm:grid-cols-2 gap-x-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Montant versé</label>
              <UInput color="blue" variant="outline" v-model="invoice.montantVerse" type="number" min="0" :max="total" class="mt-1" />
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

    <!-- Aperçu impression (inchangé) -->
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
            <td class="border p-2 text-right">{{ formatCurrency(item.quantity * item.price) }}</td>
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
