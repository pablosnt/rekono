<template>
  <v-divider v-if="divider && item.tags.length > 0" class="mt-3 mb-3" />
  <!-- <v-chip-group v-if="item.tags.length > 0" selected-class="v-chip" center-active> -->
  <div v-if="item.tags.length > 0" class="d-flex justify-center ga-2">
    <v-chip v-for="tag in item.tags" :key="tag" size="small" selected>
      {{ tag }}
    </v-chip>
  </div>
  <!-- </v-chip-group> -->
</template>

<script setup lang="ts">
defineProps({ item: Object, divider: Boolean });
</script>
