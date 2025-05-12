<template>
  <div class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md space-y-2">
    <TransitionGroup name="slide-fade" tag="div">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="mx-4 p-4 rounded-lg shadow-lg flex items-center"
        :class="{
          'bg-green-100 text-green-800': toast.type === 'success',
          'bg-red-100 text-red-800': toast.type === 'error',
          'bg-blue-100 text-blue-800': toast.type === 'info'
        }"
      >
        <UIcon
          :name="getIcon(toast.type)"
          class="mr-3 text-lg"
        />
        <span class="flex-1">{{ toast.message }}</span>
        <UButton
          icon="i-heroicons-x-mark"
          color="gray"
          variant="ghost"
          size="xs"
          @click="removeToast(toast.id)"
        />
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useNotification } from '../types/useNotification';

const { toasts } = useNotification();

const getIcon = (type: string) => {
  switch (type) {
    case 'success': return 'i-heroicons-check-circle';
    case 'error': return 'i-heroicons-exclamation-circle';
    default: return 'i-heroicons-information-circle';
  }
};

const removeToast = (id: string) => {
  toasts.value = toasts.value.filter(t => t.id !== id);
};
</script>
