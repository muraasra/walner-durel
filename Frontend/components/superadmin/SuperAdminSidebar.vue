<script setup lang="ts">
import { NAVIGATION_ITEMS_SUPERADMIN } from "~/constants";
// Fonction de déconnexion
import { useAuthStore } from '~/stores/auth'
const auth = useAuthStore();
function handleLogout() {
  auth.logout()
}
</script>

  <template>
    <div
      class="hidden z-10 md:block fixed w-[250px] h-full py-5 px-2 border-r dark:border-r-gray-600 border-r-gray-200 
      overflow-y-auto scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-400 hover:scrollbar-thumb-gray-500 "
    >
      <div class="flex items-center justify-center">
        <NuxtLink href="/" class="text-lg md:text-2xl font-extrabold pb-3"
          ><span class="text-blue-400">Walner</span>Tech Super Admin </NuxtLink>
      </div>
      <div class="px-1 mt-4">
        <div
          v-for="navigation in NAVIGATION_ITEMS_SUPERADMIN"
          class="space-y-1 mb-3 pb-3 border-b last:border-b-0 dark:border-b-gray-600 border-b-gray-200"
        >
          <NuxtLink
            active-class="bg-blue-400 text-white"
            v-for="nav in navigation"
            :href="nav.link"
            class="flex items-center gap-x-2 cursor-pointer px-4 py-4 hover:bg-blue-400 rounded-md hover:text-white transition-all"
          >
            <UIcon :name="nav.icon" class="w-5 h-5" />
            <span v-if="nav.name=='Logout'" ><button @click="handleLogout" >
              {{ nav.name }}
  </button></span>
            <span v-else class="text-sm">{{ nav.name }}</span>
          </NuxtLink>
        </div>
      </div>
    </div>
  </template>
  