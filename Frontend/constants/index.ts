import type { Produit } from "@/types"

export const NAVIGATION_ITEMS = [
  [
    {
      name: "Stock des Produits",
      link: "/stock_produit",
      icon: "i-heroicons-square-2-stack",
    },
  ],
  [
    {
      name: "Facturation",
      link: "/facturation",
      icon: "i-heroicons-document-currency-dollar",
    },
    {
      name: "Liste des factures",
      link: "/listes-factures",
      icon: "i-heroicons-clipboard-document-list",
    },
  ],
  [
    {
      name: "Transfert",
      link: "/transfert",
      icon: "i-heroicons-arrows-right-left",
    },
  ],
  [
    {
      name: "Logout",
      link: "",
      icon: "i-heroicons-power",
    },
  ],
  // [
  //   {
  //     name: "Guide",
  //     link: "/guide",
  //     icon: "i-heroicons-book-open",
  //   },
  // ],
];

export const NAVIGATION_ITEMS_ADMIN = [
  [
    {
      name: "Produits",
      link: "/produits",
      icon: "i-heroicons-squares-plus",
    },

    {
      name: "Stock des Produits",
      link: "/stock_produit",
      icon: "i-heroicons-square-2-stack",
    },
  ],
    [ 
    {
      name: "Partenaires",
      link: "/partenaires",
      icon: "i-heroicons-user-group",
    },
  ],
  [ 
    {
      name: "Facturation",
      link: "/facturation",
      icon: "i-heroicons-document-currency-dollar",
    },    
    {
      name: "Liste des factures",
      link: "/listes-factures",
      icon: "i-heroicons-clipboard-document-list",
    },
  ],
  [
    {
      name: "Transfert",
      link: "/transfert",
      icon: "i-heroicons-arrows-right-left",
    },
  ],
  // [
  //   {
  //     name: "Guide",
  //     link: "/guide",
  //     icon: "i-heroicons-book-open",
  //   },
  // ],
  [
    {
      name: "Logout",
      link: "",
      icon: "i-heroicons-power",
    },
  ],
];

export const NAVIGATION_ITEMS_SUPERADMIN = [
  [
    {
      name: "Dashboard",
      link: "/",
      icon: "i-heroicons-rectangle-group",
    },
    {
      name: "Produits",
      link: "/produits",
      icon: "i-heroicons-squares-plus",
    },
    {
      name: "Stock des Produits",
      link: "/stock_produit",
      icon: "i-heroicons-square-2-stack",
    },
  ],
  [
    {
      name: "Utilisateurs",
      link: "/utilisateurs",
      icon: "i-heroicons-user",
    },
    {
      name: "Journal",
      link: "/journal",
      icon: "i-heroicons-clipboard-document-list",
    },
  ],
  [ 
    {
      name: "Partenaires",
      link: "/partenaires",
      icon: "i-heroicons-user-group",
    },
  ],
  [ 
    {
      name: "Facturation",
      link: "/facturation",
      icon: "i-heroicons-document-currency-dollar",
    },    
    {
      name: "Liste des factures",
      link: "/listes-factures",
      icon: "i-heroicons-clipboard-document-list",
    },
  ],
  [
    {
      name: "Transfert",
      link: "/transfert",
      icon: "i-heroicons-arrows-right-left",
    },
  ],
  // [
  //   {
  //     name: "Guide",
  //     link: "/guide",
  //     icon: "i-heroicons-book-open",
  //   },
  // ],
  [
    {
      name: "Logout",
      link: "",
      icon: "i-heroicons-power",
    },
  ],
];

export const PRODUCTS_DATA: Produit[] = [
  {
    id: "PD-001",
    nomProduit: "Souris sans fil",
    imageProduit: "/img/souris_sans_fil.png",
    prix: 15990,
    dateCommande: "2024-11-12T14:32:00Z",
    quantiteTotale: 100,
    quantiteCommandee: 5,
    statut: "Expédié",
    lieuCommande: "Yaoundé",
    categorie: "Électronique",
    reference: "WM-2024-001",
    descriptionProduit: "Souris ergonomique avec DPI réglable et longue autonomie.",
    nomClient: "Jean Dupont",
    couleursDisponibles: ["#000000", "#FFFFFF", "#FF4500"],
    estPartenaire: true,
  },
  {
    id: "PD-002",
    nomProduit: "Clavier mécanique",
    imageProduit: "/img/clavier_mecanique.png",
    prix: 49990,
    dateCommande: "2024-10-05T09:21:00Z",
    quantiteTotale: 50,
    quantiteCommandee: 2,
    statut: "En attente",
    lieuCommande: "Bafoussam",
    categorie: "Électronique",
    reference: "KB-2024-002",
    descriptionProduit: "Clavier mécanique avec rétroéclairage RGB et switches silencieux.",
    nomClient: "Alice Mballa",
    couleursDisponibles: ["#FF0000", "#00FF00", "#0000FF"],
    estPartenaire: false,
  },
  {
    id: "PD-003",
    nomProduit: "Casque Bluetooth",
    imageProduit: "/img/casque_bluetooth.png",
    prix: 29990,
    dateCommande: "2024-09-25T16:45:00Z",
    quantiteTotale: 75,
    quantiteCommandee: 3,
    statut: "Livré",
    lieuCommande: "Yaoundé",
    categorie: "Accessoires",
    reference: "HS-2024-003",
    descriptionProduit: "Casque sans fil avec réduction de bruit et autonomie longue durée.",
    nomClient: "Bernard Nguefack",
    couleursDisponibles: ["#000000", "#888888"],
    estPartenaire: true,
  },
  {
    id: "PD-004",
    nomProduit: "Chargeur rapide 65W",
    imageProduit: "/img/chargeur_rapide.png",
    prix: 14990,
    dateCommande: "2024-08-30T12:15:00Z",
    quantiteTotale: 120,
    quantiteCommandee: 10,
    statut: "Expédié",
    lieuCommande: "Bafoussam",
    categorie: "Électronique",
    reference: "CH-2024-004",
    descriptionProduit: "Chargeur rapide compatible avec plusieurs appareils.",
    nomClient: "Esther Tchatchoua",
    couleursDisponibles: ["#FFFFFF", "#000000"],
    estPartenaire: false,
  },
  {
    id: "PD-005",
    nomProduit: "Power Bank 20000mAh",
    imageProduit: "/img/power_bank.png",
    prix: 24990,
    dateCommande: "2024-07-18T08:10:00Z",
    quantiteTotale: 60,
    quantiteCommandee: 4,
    statut: "Livré",
    lieuCommande: "Yaoundé",
    categorie: "Accessoires",
    reference: "PB-2024-005",
    descriptionProduit: "Batterie externe haute capacité pour charger plusieurs appareils.",
    nomClient: "Arsène Fotso",
    couleursDisponibles: ["#000000", "#D3D3D3"],
    estPartenaire: true,
  },
  {
    id: "PD-006",
    nomProduit: "Écran 24 pouces LED",
    imageProduit: "/img/ecran_led.png",
    prix: 119990,
    dateCommande: "2024-06-10T17:55:00Z",
    quantiteTotale: 30,
    quantiteCommandee: 1,
    statut: "En attente",
    lieuCommande: "Bafoussam",
    categorie: "Électronique",
    reference: "MN-2024-006",
    descriptionProduit: "Écran LED Full HD avec design ultra-fin.",
    nomClient: "Sylvie Kameni",
    couleursDisponibles: ["#000000"],
    estPartenaire: false,
  },
  {
    id: "PD-007",
    nomProduit: "Imprimante multifonction",
    imageProduit: "/img/imprimante.png",
    prix: 149990,
    dateCommande: "2024-05-22T14:00:00Z",
    quantiteTotale: 20,
    quantiteCommandee: 2,
    statut: "Expédié",
    lieuCommande: "Yaoundé",
    categorie: "Bureautique",
    reference: "PRT-2024-007",
    descriptionProduit: "Imprimante laser couleur avec fonction scanner et photocopie.",
    nomClient: "David Ebogo",
    couleursDisponibles: ["#FFFFFF", "#000000"],
    estPartenaire: true,
  },
  {
    id: "PD-008",
    nomProduit: "Sacoche pour ordinateur",
    imageProduit: "/img/sacoche.png",
    prix: 9990,
    dateCommande: "2024-04-15T09:30:00Z",
    quantiteTotale: 90,
    quantiteCommandee: 7,
    statut: "Livré",
    lieuCommande: "Bafoussam",
    categorie: "Accessoires",
    reference: "BG-2024-008",
    descriptionProduit: "Sacoche résistante et imperméable pour ordinateurs portables.",
    nomClient: "Henri Kouam",
    couleursDisponibles: ["#000000", "#808080"],
    estPartenaire: false,
  },
  {
    id: "PD-009",
    nomProduit: "Clé USB 128 Go",
    imageProduit: "/img/cle_usb.png",
    prix: 12990,
    dateCommande: "2024-03-20T13:20:00Z",
    quantiteTotale: 150,
    quantiteCommandee: 20,
    statut: "Expédié",
    lieuCommande: "Yaoundé",
    categorie: "Stockage",
    reference: "USB-2024-009",
    descriptionProduit: "Clé USB ultra-rapide avec transfert sécurisé.",
    nomClient: "Lionel Mvondo",
    couleursDisponibles: ["#0000FF", "#FF0000"],
    estPartenaire: true,
  },
  {
    id: "PD-010",
    nomProduit: "Smartphone Android",
    imageProduit: "/img/smartphone.png",
    prix: 199990,
    dateCommande: "2024-02-05T15:45:00Z",
    quantiteTotale: 25,
    quantiteCommandee: 1,
    statut: "En attente",
    lieuCommande: "Bafoussam",
    categorie: "Téléphonie",
    reference: "SP-2024-010",
    descriptionProduit: "Smartphone Android avec écran AMOLED et double SIM.",
    nomClient: "Marthe Tamo",
    couleursDisponibles: ["#000000", "#FFFFFF"],
    estPartenaire: false,
  }
];

