<script setup lang="ts">
import { z } from "zod";
import type { FormSubmitEvent } from "#ui/types";
import type { Product } from "~/types";

const props = defineProps<{ product: Product }>();

const isOpen = ref(false);
const emit = defineEmits(["editer-produit"]);

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
  actif: props.product.actif,
});

async function onSubmit(event: FormSubmitEvent<Schema>) {
  isOpen.value = false;
  emit("editer-produit", {
    ...event.data,
    id: props.product.id,
  });
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

          <UFormGroup label="Prix" name="prix">
            <UInput type="number" v-model="state.prix" placeholder="Prix" />
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
