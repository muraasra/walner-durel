export type Produit = {
  id: number;
  reference: string;
  category: string;
  nom: string;
  description: string;
  quantite: number;
  prix: number;
  prix_achat: number;
  actif: boolean;
  boutique: number;
  // Champs spécifiques pour les ordinateurs
  ram?: string;
  stockage?: string;
  processeur?: string;
  annee?: string;
  marque?: string;
  modele?: string;
  systeme_exploitation?: string;
};


export type Partenaire = {
  id: string;
  nomPartenaire : string;
  prenomPartenaire : string;
  telephone: number; 
  status:string; // pour voir si ila a deja payé toutes ces dettes ou pas encore 
  boutique : boolean ;
  localisationBoutique: string;
  dateAdhesion: string;
};

