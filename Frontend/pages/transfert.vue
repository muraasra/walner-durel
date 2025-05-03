<script setup lang="ts">
import { ref } from 'vue';

// Définition du type Transfert directement dans le composant
interface Transfert {
  id: number;
  articleId: number;
  articleName: string;
  fromBoutiqueId: number;
  toBoutiqueId: number;
  quantity: number;
  status: 'pending' | 'completed';
}

// Liste des transferts
const transferts = ref<Transfert[]>([]);

// État de la boîte de dialogue
const showDialog = ref(false);

// État du formulaire pour un nouveau transfert
const newTransfert = ref<Omit<Transfert, 'id' | 'status'>>({
  articleId: 0,
  articleName: '',
  fromBoutiqueId: 0,
  toBoutiqueId: 0,
  quantity: 1,
});

// Fonction pour ouvrir la boîte de dialogue
const openDialog = () => {
  showDialog.value = true;
};

// Fonction pour ajouter un transfert après validation du formulaire
const addTransfert = () => {
  transferts.value.push({
    id: Date.now(),
    ...newTransfert.value,
    status: 'pending',
  });

  // Réinitialiser le formulaire
  newTransfert.value = { articleId: 0, articleName: '', fromBoutiqueId: 0, toBoutiqueId: 0, quantity: 1 };
  showDialog.value = false;
};

// Fonction pour marquer un transfert comme complété
const completeTransfert = (id: number) => {
  const transfert = transferts.value.find(t => t.id === id);
  if (transfert) transfert.status = 'completed';
};
</script>

<template>
  <section class="mt-5 px-6">
    <h2 class="text-xl md:text-3xl font-bold text-blue-400">Transferts</h2>

    <!-- Bouton Nouveau Transfert -->
    <div class="flex justify-end mb-4">
      <UButton @click="openDialog" color="blue" size="lg">
        Nouveau Transfert
      </UButton>
    </div>

    <!-- Boîte de dialogue pour le formulaire -->
    <UModal v-model="showDialog">
      <div class="p-6">
        <h3 class="text-lg font-semibold mb-4">Créer un Nouveau Transfert</h3>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Nom de l'article</label>
          <UInput  color="blue" v-model="newTransfert.articleName" placeholder="Ex: Ordinateur" />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Boutique Source</label>
          <UInput color="blue" v-model="newTransfert.fromBoutiqueId" type="number" min="1" placeholder="ID de la boutique source" />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Boutique Destination</label>
          <UInput color="blue" v-model="newTransfert.toBoutiqueId" type="number" min="1" placeholder="ID de la boutique destination" />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Quantité</label>
          <UInput color="blue" v-model="newTransfert.quantity" type="number" min="1" />
        </div>

        <div class="flex justify-end space-x-2">
          <UButton @click="showDialog = false" color="gray">Annuler</UButton>
          <UButton @click="addTransfert" color="blue">Valider</UButton>
        </div>
      </div>
    </UModal>

    <!-- Liste des Transferts -->
    <div class="border rounded-lg shadow-lg p-6">
      <div v-if="transferts.length === 0" class="text-center text-gray-500">
        Aucune demande de transfert.
      </div>

      <div v-else>
        <div
          v-for="transfert in transferts"
          :key="transfert.id"
          class="flex justify-between items-center mb-4 p-4 border-b"
        >
          <div>
            <p class="font-semibold">{{ transfert.articleName }}</p>
            <p class="text-sm text-gray-500">
              De: Boutique {{ transfert.fromBoutiqueId }} à Boutique {{ transfert.toBoutiqueId }}
            </p>
            <p class="text-sm text-gray-500">Quantité: {{ transfert.quantity }}</p>
          </div>

          <div>
            <span
              :class="{
                'text-red-400': transfert.status === 'pending',
                'text-green-400': transfert.status === 'completed',
              }"
              class="font-medium"
            >
              {{ transfert.status === 'pending' ? 'En attente' : 'Complété' }}
            </span>
            <div v-if="transfert.status === 'pending'">
              <UButton
                @click="completeTransfert(transfert.id)"
                color="blue"
                size="sm"
              >
                Marquer comme complété
              </UButton>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
