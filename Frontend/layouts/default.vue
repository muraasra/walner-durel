<script setup>
import { ref, computed } from "vue";
import AdminSidebar from "@/components/admin/AdminSidebar.vue";
import Sidebar from "@/components/Sidebar.vue";
import notification from "@/components/notification.vue";


const userRole = ref("admin"); // "admin" ou "employe"

// Choisir la bonne sidebar
const SidebarComponent = computed(() => (userRole.value === "admin" ? AdminSidebar : Sidebar));

const toasts = ref([]);
provide('toasts', toasts);

</script>

<template>
  <main class="w-full flex h-full">
    <component :is="SidebarComponent" />
    <div class="flex-1 h-full pl-0 md:pl-[250px] pb-10">
      <slot />
      <div class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 space-y-2 w-full max-w-md pointer-events-none">
      <notification />
    </div>
    </div>
  </main>
</template>

