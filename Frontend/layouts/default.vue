<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import AdminSidebar from "@/components/admin/AdminSidebar.vue";
import SuperAdminSidebar from "@/components/superadmin/SuperAdminSidebar.vue";
import Sidebar from "@/components/Sidebar.vue";
import notification from "@/components/notification.vue";

const router = useRouter();
const user = ref(null);

if (process.client) {
  const userData = localStorage.getItem('user');
  if (userData) {
    user.value = JSON.parse(userData);
  }
}

const userRole = computed(() => user.value?.role || "user");

const SidebarComponent = computed(() => {
  if (userRole.value === "admin") {
    return AdminSidebar;
  } else if (userRole.value === "superadmin") {
    return SuperAdminSidebar;
  }
  return Sidebar;
});

onMounted(() => {
  if (user.value) {
    if (user.value.role === "admin") {
      router.push("/admin/");
    } else if (user.value.role === "superadmin") {
      router.push("/superadmin/");
    } else {
      router.push("/user/");
    }
  }
});

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

