<!-- <script setup lang="ts">
import Sidebar from "~/components/Sidebar.vue";
</script>

<template>
  <main class="w-full flex h-full">
    <Sidebar />
    <div class="flex-1 h-full pl-0 md:pl-[200px] pb-10">
      <slot />
    </div>
  </main> 
</template>-->

<script setup>
import { ref, computed } from "vue";
import AdminSidebar from "@/components/admin/AdminSidebar.vue";
import Sidebar from "@/components/Sidebar.vue";


const userRole = ref("admin"); // "admin" ou "employe"

// Choisir la bonne sidebar
const SidebarComponent = computed(() => (userRole.value === "admin" ? AdminSidebar : Sidebar));
</script>

<template>
  <main class="w-full flex h-full">
    <component :is="SidebarComponent" />
    <div class="flex-1 h-full pl-0 md:pl-[250px] pb-10">
      <slot />
    </div>
  </main>
</template>

