<script setup lang="ts">
import creer_produit_modal from "@/components/produits/creer_produit_modal.vue";
import produit_card from "@/components/produits/produit_card.vue";

import { useApi } from '../stores/useApi';
import { useNotification } from '~/types/useNotification';

const { success, errors } = useNotification();

// --- Types
export type Produit = {
    id: number;
    nom: string;
    reference?: string;                 // <- optionnelle
    category: string;
    prix: number;
    prix_achat?: number;
    quantite?: number;
    description?: string;
    actif?: boolean;
    boutique: number;                   // tu imposes 1 côté modal

    // optionnels (texte) — souvent null côté API si vides
    ram?: string | null;
    stockage?: string | null;
    processeur?: string | null;
    marque?: string | null;
    modele?: string | null;
    systeme_exploitation?: string | null;

    // optionnel (numérique)
    annee?: number | null;
};

type ProductDraft = Omit<Produit, 'id'>;

// --- State
const { public: { apiBase = 'http://127.0.0.1:8000/api' } } = useRuntimeConfig()
const produits = ref<Produit[]>([])
const loading = ref(false)
const search = ref('')

// --- Fetch initial
async function fetchProduits() {
    loading.value = true
    const { data, error } = await useApi<Produit[]>(`${apiBase}/produits/`, { method: 'GET' })
    if (!error.value && Array.isArray(data.value)) {
        produits.value = data.value
    } else {
        console.error('Erreur fetch produits', error.value)
    }
    loading.value = false
}
onMounted(fetchProduits)

// --- Ajout depuis le modal
async function ajouterProduit(payload?: ProductDraft) {
    if (!payload) {
        errors('Données manquantes depuis le formulaire.')
        return
    }

    // Déduplication
    const newRef = (payload.reference || '').trim().toLowerCase()
    if (newRef && produits.value.some(p => (p.reference || '').trim().toLowerCase() === newRef)) {
        errors('Un produit avec cette référence existe déjà.')
        return
    }

    try {
        const { data, error: apiError } = await useApi<Produit>(`${apiBase}/produits/`, {
            method: 'POST',
            body: payload
        })

        if (apiError.value) {
            errors('Création échouée : ' + JSON.stringify(apiError.value))
            return
        }

        if (data.value) {
            produits.value.unshift(data.value)
            success('Produit ajouté avec succès')
        } else {
            errors('Réponse du serveur vide')
        }
    } catch (e) {
        console.error(e)
        errors('Erreur réseau pendant la création')
    }
}

// * Fonction pour éditer un produit
type ComputerField = 'ram' | 'stockage' | 'processeur' | 'marque' | 'modele' | 'systeme_exploitation';
const COMPUTER_FIELDS: ComputerField[] = ['ram', 'stockage', 'processeur', 'marque', 'modele', 'systeme_exploitation'];

const normalizeText = (v: unknown): string | null => {
  if (v == null) return null
  const s = String(v).trim()
  return s === '' ? null : s
}

const normalizeYear = (v: unknown): number | null => {
  if (v == null || v === '') return null
  const n = typeof v === 'string' ? parseInt(v, 10) : Number(v)
  return Number.isFinite(n) ? n : null
}

function buildProduitPatch(p: Produit): Partial<Produit> {
  const { id, ...rest } = p

  const patch: Partial<Produit> = {
    nom: (rest.nom || '').trim(),
    reference: (rest.reference || '').trim() || undefined,
    category: (rest.category || '').trim(),

    prix: Number(rest.prix),
    prix_achat: rest.prix_achat != null ? Number(rest.prix_achat) : undefined,
    quantite: rest.quantite != null ? Number(rest.quantite) : undefined,

    description: (rest.description || '').trim() || undefined,
    actif: typeof rest.actif === 'boolean' ? rest.actif : true,

    boutique: 1,

    // champs "ordi"
    annee: normalizeYear(rest.annee as unknown),
    ram: normalizeText(rest.ram),
    stockage: normalizeText(rest.stockage),
    processeur: normalizeText(rest.processeur),
    marque: normalizeText(rest.marque),
    modele: normalizeText(rest.modele),
    systeme_exploitation: normalizeText(rest.systeme_exploitation),
  }

  // Si ce n’est pas un ordinateur, on met les champs ordi à null (cohérent avec le back)
  if (patch.category !== 'ordinateur') {
    for (const f of COMPUTER_FIELDS) (patch as any)[f] = null
    patch.annee = null
  }

  // Retirer les clés null/undefined pour un PATCH minimal
  Object.keys(patch).forEach((k) => (patch as any)[k] == null && delete (patch as any)[k])

  return patch
}

// * Fonction pour modifier un produit
async function editerProduit(updatedProduit: Produit) {
  try {
    const body = buildProduitPatch(updatedProduit)

    const { data, error: apiError } = await useApi<Produit>(
      `${apiBase}/produits/${updatedProduit.id}/`,
      { method: 'PATCH', body }
    )

    if (apiError.value) {
      console.error("Erreur lors de la mise à jour du produit", apiError.value)
      errors('Modification échouée : ' + JSON.stringify(apiError.value))
      return
    }

    if (data.value) {
      const idx = produits.value.findIndex(p => p.id === data.value!.id)
      if (idx !== -1) {
        produits.value[idx] = data.value!
        produits.value.sort((a, b) => b.id - a.id)
      }
      success("Produit modifié avec succès!")
    } else {
      errors("Réponse du serveur vide")
    }
  } catch (err) {
    console.error("Exception lors de la modification du produit:", err)
    errors("Une erreur est survenue lors de la modification du produit")
  }
}



// * Fonction pour supprimer un produit
async function supprimerProduit(deletedProduit: Produit) {
    const { error } = await useApi(
        `http://127.0.0.1:8000/api/produits/${deletedProduit.id}/`,
        {
            method: 'DELETE',
        }
    );

    if (!error.value) {
        const index = produits.value?.findIndex((p) => p.id === deletedProduit.id);
        if (index !== undefined && index !== -1) {
            produits.value?.splice(index, 1);
            // Sort the products in descending order after deleting
            produits.value.sort((a, b) => b.id - a.id);
        }
    } else {
        console.error("Erreur lors de la suppression du produit", error.value);
    }
}

// Sort products in descending order by ID after initial fetch
if (produits.value) {
    produits.value.sort((a, b) => b.id - a.id);
}
</script>

<template>
    <section class="mt-5 px-6">
        <div class="flex items-center gap-x-4 justify-between">
            <h2 class="text-xl md:text-3xl font-bold text-blue-400">Produits</h2>
            <creer_produit_modal @creer-produit="ajouterProduit($event)" />
        </div>

        <div class="mt-7 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-5 gap-y-6">
            <produit_card v-for="produit in produits" :key="produit.id" :product="produit"
                @editer-produit="editerProduit" @delete-product="supprimerProduit" />
        </div>
    </section>
</template>
