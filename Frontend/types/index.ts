export type Produit = {
  id: number;
  reference: string;
  category: string;
  nom: string;
  description: string;
  quantite: number;
  prix: number;
  actif: boolean;
  boutique: number;
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

