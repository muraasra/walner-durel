const isSuperAdmin = computed(() => {
  return userRole.value === "superadmin";
});

<template>
  <nav>
    <!-- ... existing navigation items ... -->
    
    <!-- Lien vers le journal pour les superadmin -->
    <NuxtLink
      v-if="isSuperAdmin"
      to="/journal"
      class="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100"
    >
      <UIcon name="i-heroicons-clipboard-document-list" class="w-5 h-5 mr-2" />
      Journal des opérations
    </NuxtLink>
    
    <!-- ... rest of the navigation ... -->
  </nav>
</template> 