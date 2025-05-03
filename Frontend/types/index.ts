export type Produit = {
  id: string;
  nomProduit: string;
  imageProduit: string;
  prix: number;
  dateCommande: string;
  quantiteTotale: number;
  quantiteCommandee: number;
  statut: string;
  lieuCommande: string;
  categorie: string;
  reference: string; // CODE BARRE
  descriptionProduit: string;
  nomClient: string;
  couleursDisponibles: string[];
  estPartenaire : boolean;
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

