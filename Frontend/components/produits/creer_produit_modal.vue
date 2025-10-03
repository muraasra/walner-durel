<script setup lang="ts">
import { z } from "zod";
import type { FormSubmitEvent } from "#ui/types";

type ProductDraft = {
  nom: string;
  reference?: string;
  category: string;
  prix: number;
  prix_achat?: number;
  quantite?: number;
  description?: string;
  actif?: boolean;

  // optionnels
  marque?: string | null;
  modele?: string | null;
  processeur?: string | null;
  ram?: string | null;
  stockage?: string | null;
  systeme_exploitation?: string | null;
  annee?: number | null;

  // imposé côté front
  boutique: number; // on mettra 1 à l’envoi
};

const emit = defineEmits<{
  (e: 'creer-produit', payload: ProductDraft): void
}>();

// Helpers: "" -> null (texte), "" -> null sinon Number (numérique)
const emptyToNull = (v: any) => (v === '' || typeof v === 'undefined' ? null : v);
const numOrNull   = (v: any) => (v === '' || v === null || typeof v === 'undefined' ? null : Number(v));


/* ---------- Superadmin (afficher prix_achat) ---------- */
const isSuperAdmin = computed(() => {
  if (!process.client) return false
  try {
    const u = JSON.parse(localStorage.getItem('user') || 'null')
    return (u?.role || '').toLowerCase() === 'superadmin'
  } catch { return false }
})


const Schema = z.object({
  nom: z.string().min(1, 'Nom requis'),
  reference: z.string().optional(),
  category: z.string().min(1, 'Catégorie requise'),
  prix: z.number().positive('Prix > 0'),
  prix_achat: z.number().positive('Prix achat > 0').optional(),
  quantite: z.number().int().nonnegative().default(0),
  description: z.string().optional(),
  actif: z.boolean().default(true),

  marque: z.string().optional(),
  modele: z.string().optional(),
  processeur: z.string().optional(),
  ram: z.string().optional(),
  stockage: z.string().optional(),
  systeme_exploitation: z.string().optional(),
  annee: z.union([z.number().int(), z.null()]).optional(),
});
type Schema = z.output<typeof Schema>;

const isOpen = ref(false);

const state = reactive<Schema>({
  nom: '',
  reference: '',
  category: '',
  prix: 0,
  prix_achat: undefined,
  quantite: 0,
  description: '',
  actif: true,
  marque: '',
  modele: '',
  processeur: '',
  ram: '',
  stockage: '',
  systeme_exploitation: '',
  annee: null,
});

function open() {
  Object.assign(state, {
    nom: '', reference: '', category: '',
    prix: 0, prix_achat: undefined, quantite: 0,
    description: '', actif: true,
    marque: '', modele: '', processeur: '', ram: '', stockage: '',
    systeme_exploitation: '', annee: null,
  } as Schema);
  isOpen.value = true;
}

async function onSubmit(e: FormSubmitEvent<Schema>) {
  // prépare un payload propre pour le parent
  const productData: ProductDraft = {
    nom: e.data.nom.trim(),
    reference: (e.data.reference || '').trim(),
    category: e.data.category.trim(),
    prix: Number(e.data.prix),
    prix_achat: e.data.prix_achat !== undefined ? Number(e.data.prix_achat) : undefined,
    quantite: Number(e.data.quantite ?? 0),
    actif: !!e.data.actif,
    description: (e.data.description || '').trim(),

    marque: emptyToNull(e.data.marque),
    modele: emptyToNull(e.data.modele),
    processeur: emptyToNull(e.data.processeur),
    ram: emptyToNull(e.data.ram),
    stockage: emptyToNull(e.data.stockage),
    systeme_exploitation: emptyToNull(e.data.systeme_exploitation),

    annee: numOrNull(e.data.annee),

    // 👉 exigence : imposer boutique = 1 côté front
    boutique: 1,
  };

  // Nettoyage: retire les clés null/undefined (optionnel)
  Object.keys(productData).forEach((k) => {
    const v = (productData as any)[k];
    if (v === null || typeof v === 'undefined') delete (productData as any)[k];
  });

  // ✅ ÉMETTRE LE PAYLOAD AU PARENT
  emit('creer-produit', productData);
  isOpen.value = false;
}
</script>

<template>
  <div>
    <UButton color="blue" @click="open">Creer un nouveau produit</UButton>

    <UModal v-model="isOpen">
      <div class="p-4 space-y-4">
        <h3 class="text-lg font-semibold">Créer un produit</h3>

        <UForm :state="state" :schema="Schema" @submit="onSubmit" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <UFormGroup label="Nom *" name="nom">
            <UInput v-model.trim="state.nom" placeholder="Ex: Dell Latitude" color="blue"/>
          </UFormGroup>

          <UFormGroup label="Référence" name="reference">
            <UInput v-model.trim="state.reference" placeholder="SKU / Réf" color="blue"/>
          </UFormGroup>

          <UFormGroup label="Categorie" name="category">
            <USelect
              v-model="state.category"
              :options="[
                { value: 'telephone', label: 'Téléphone' },
                { value: 'ordinateur', label: 'Ordinateur' },
                { value: 'accessoire', label: 'Accessoire' },
                { value: 'ecran', label: 'Écran' },
                { value: 'imprimante', label: 'Imprimante' },
                { value: 'tablette', label: 'Tablette' },
                { value: 'casque', label: 'Casque' },
                { value: 'clavier', label: 'Clavier' },
                { value: 'souris', label: 'Souris' },
                { value: 'modem', label: 'Modem' },
                { value: 'disquedur', label: 'Disque dur' },
                { value: 'cleusb', label: 'Clé USB' },
                { value: 'autre', label: 'Autre' },
              ]"
              placeholder="Sélectionner une catégorie"
              color="blue"
            />
          </UFormGroup>

          <UFormGroup label="Prix (vente) *" name="prix">
            <UInput type="number" v-model.number="state.prix" min="0" step="0.01" color="blue"/>
          </UFormGroup>

          <UFormGroup v-if="isSuperAdmin" label="Prix d'achat" name="prix_achat">
            <UInput type="number" v-model.number="state.prix_achat" min="0" step="0.01" color="blue"/>
          </UFormGroup>

          <UFormGroup label="Quantité" name="quantite">
            <UInput type="number" v-model.number="state.quantite" min="0" step="1" color="blue"/>
          </UFormGroup>

          <UFormGroup label="Description" name="description" class="md:col-span-2">
            <UTextarea v-model.trim="state.description" :rows="3" placeholder="Détails du produit…" color="blue"/>
          </UFormGroup>




          <!-- si c'est un Ordinateur -->
          <template v-if="state.category === 'ordinateur'">

            <UFormGroup label="Marque" name="marque">
              <UInput v-model.trim="state.marque" placeholder="Ex: Dell, HP" color="blue"/>
            </UFormGroup>

            <UFormGroup label="Modèle" name="modele">
              <UInput v-model.trim="state.modele" placeholder="Ex: Latitude 5420" color="blue"/>
            </UFormGroup>

            <UFormGroup label="Processeur" name="processeur">
              <UInput v-model.trim="state.processeur" placeholder="Ex: i5-1145G7" color="blue"/>
            </UFormGroup>

            <UFormGroup label="RAM" name="ram">
              <UInput v-model.trim="state.ram" placeholder="Ex: 16 Go" color="blue"/>
            </UFormGroup>

            <UFormGroup label="Stockage" name="stockage">
              <UInput v-model.trim="state.stockage" placeholder="Ex: 512 Go SSD" color="blue"/>
            </UFormGroup>

            <UFormGroup label="Système d'exploitation" name="systeme_exploitation">
              <UInput v-model.trim="state.systeme_exploitation" placeholder="Ex: Windows 11" color="blue"/>
            </UFormGroup>
          
            <UFormGroup label="Année (optionnel)" name="annee">
              <UInput type="number" :value="state.annee ?? undefined" @input="state.annee = $event.target.value ? Number($event.target.value) : null" min="1900" max="2100" step="1" color="blue"/>
            </UFormGroup>
          </template>

          <div class="md:col-span-2">
            <UButton type="submit" color="blue">Créer le produit</UButton>
          </div>
        </UForm>
      </div>
    </UModal>
  </div>
</template>