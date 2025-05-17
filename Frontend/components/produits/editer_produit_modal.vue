<script setup lang="ts">
import { z } from "zod";
import type { FormSubmitEvent } from "#ui/types";
import type { Product } from "~/types";
import { useAuthStore } from '@/stores/auth'
import { useNotification } from '~/types/useNotification';

const auth = useAuthStore()
const { success, error } = useNotification();

const props = defineProps<{ product: Product }>();

const isOpen = ref(false);
const emit = defineEmits(["editer-produit"]);

// Computed pour vérifier si l'utilisateur est super-admin
const isSuperAdmin = computed(() => {
  return auth.user?.role === 'superadmin';
});

const categoryOptions = [
  { value: "telephone", label: "Téléphone" },
  { value: "ordinateur", label: "Ordinateur" },
  { value: "accessoire", label: "Accessoire" },
  { value: "ecran", label: "Écran" },
  { value: "imprimante", label: "Imprimante" },
  { value: "tablette", label: "Tablette" },
  { value: "casque", label: "Casque" },
  { value: "clavier", label: "Clavier" },
  { value: "souris", label: "Souris" },
  { value: "modem", label: "Modem" },
  { value: "disquedur", label: "Disque dur" },
  { value: "cleusb", label: "Clé USB" },
  { value: "autre", label: "Autre" },
];

const schema = z.object({
  reference: z.string().min(1, "La référence est requise"),
  category: z.enum([
    "telephone",
    "ordinateur",
    "accessoire",
    "ecran",
    "imprimante",
    "tablette",
    "casque",
    "clavier",
    "souris",
    "modem",
    "disquedur",
    "cleusb",
    "autre",
  ]),
  nom: z.string().min(1, "Le nom est requis"),
  description: z.string().min(1, "La description est requise"),
  quantite: z.number(),
  prix: z.number(),
  prix_achat: z.number().optional(),
  actif: z.boolean(),
});

type Schema = z.output<typeof schema>;

const state = ref({
  reference: props.product.reference,
  category: props.product.category,
  nom: props.product.nom,
  description: props.product.description,
  quantite: props.product.quantite,
  prix: props.product.prix,
  prix_achat: props.product.prix_achat || 0,
  actif: props.product.actif,
});

async function onSubmit(event: FormSubmitEvent<Schema>) {
  try {
    if (!event.data.reference) {
      error("La référence est requise");
      return;
    }
    if (!event.data.nom) {
      error("Le nom du produit est requis");
      return;
    }
    if (!event.data.prix || event.data.prix <= 0) {
      error("Le prix de vente doit être supérieur à 0");
      return;
    }
    if (isSuperAdmin.value && event.data.prix_achat && event.data.prix_achat <= 0) {
      error("Le prix d'achat doit être supérieur à 0");
      return;
    }
    if (!event.data.category) {
      error("La catégorie est requise");
      return;
    }
    if (!event.data.quantite || event.data.quantite < 0) {
      error("La quantité doit être positive ou nulle");
      return;
    }
    if (!event.data.description) {
      error("La description est requise");
      return;
    }

    emit("editer-produit", {
      ...event.data,
      id: props.product.id,
    });

    success("Produit modifié avec succès!");
    isOpen.value = false;
  } catch (err) {
    console.error("Erreur lors de la modification du produit:", err);
    error("Une erreur est survenue lors de la modification du produit");
  }
}
</script>

<template>
  <div>
    <UButton variant="outline" @click="isOpen = true">Modifier</UButton>
    <UModal v-model="isOpen">
      <h3 class="text-center mt-4">Modifier le produit</h3>
      <div class="p-4">
        <UForm
          :schema="schema"
          :state="state"
          class="space-y-4"
          @submit="onSubmit"
        >
          <UFormGroup label="Référence" name="reference">
            <UInput v-model="state.reference" placeholder="Référence produit" />
          </UFormGroup>

          <UFormGroup label="Nom" name="nom">
            <UInput v-model="state.nom" placeholder="Nom du produit" />
          </UFormGroup>

          <UFormGroup label="Prix de vente" name="prix">
            <UInput type="number" v-model="state.prix" placeholder="Prix de vente" />
          </UFormGroup>

          <!-- Afficher le champ prix d'achat uniquement pour les super-admin -->
          <UFormGroup v-if="isSuperAdmin" label="Prix d'achat" name="prix_achat">
            <UInput type="number" v-model="state.prix_achat" placeholder="Prix d'achat" />
          </UFormGroup>

          <UFormGroup label="Quantité" name="quantite">
            <UInput type="number" v-model="state.quantite" placeholder="Quantité" />
          </UFormGroup>

          <UFormGroup label="Catégorie" name="category">
            <USelect
              v-model="state.category"
              :options="categoryOptions"
              placeholder="Sélectionnez une catégorie"
            />
          </UFormGroup>

          <UFormGroup label="Description" name="description">
            <UTextarea
              v-model="state.description"
              placeholder="Description du produit"
            />
          </UFormGroup>

          <UFormGroup label="Actif" name="actif">
            <UToggle v-model="state.actif" />
          </UFormGroup>

          <UButton type="submit">Enregistrer</UButton>
        </UForm>
      </div>
    </UModal>
  </div>
</template>
