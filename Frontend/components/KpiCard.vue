<template>
    <div :class="[
      'rounded-lg shadow-md p-6',
      `bg-${color}-50`,
      colSpan || 'col-span-1'
    ]">
      <div class="flex justify-between items-start">
        <div>
          <h3 class="text-sm font-medium text-gray-600">{{ title }}</h3>
          <p class="mt-2 text-2xl font-semibold text-gray-800">{{ value }}</p>
        </div>
        <div :class="`bg-${color}-400 text-white p-3 rounded-full`">
          <Icon :name="icon" class="w-6 h-6" />
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  defineProps<{
    title: string
    value: string | number
    icon: string
    color: 'blue' | 'green' | 'red'
    colSpan?: string
  }>()
  </script>