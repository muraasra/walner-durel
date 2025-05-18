<template>
  <div>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
// Configuration globale de l'application
useHead({
  title: 'WALNER TECH',
  meta: [
    {
      name: 'description',
      content: 'Application de gestion de stock et facturation WALNER TECH'
    }
  ],
  link: [
    {
      rel: 'icon',
      type: 'image/x-icon',
      href: '/favicon.ico'
    }
  ]
})
</script>
