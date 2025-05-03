<script setup lang="ts">
import table_produit_stock from "@/components/table_produit_stock.vue";
</script>

<template>
  <section class="mt-5 px-6">
    <h2 class="text-xl md:text-3xl font-bold text-blue-400">Produits en Stock</h2>
    <div class="mt-7 w-full">
      <table_produit_stock />
    </div>
  </section>
</template>