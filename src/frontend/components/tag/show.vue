<template>
  <v-divider v-if="divider && item.tags.length > 0" class="mt-3 mb-3" />
  <!-- <v-chip-group v-if="item.tags.length > 0" selected-class="v-chip" center-active> -->
  <div v-if="item.tags.length > 0" class="d-flex justify-center ga-2">
    <v-chip
      v-for="tag in truncate !== null
        ? item.tags.slice(0, truncate)
        : item.tags"
      :key="tag"
      size="small"
      selected
    >
      {{ tag }}
    </v-chip>
    <p v-if="truncate !== null && truncate < item.tags.length">...</p>
  </div>
  <!-- </v-chip-group> -->
</template>

<script setup lang="ts">
defineProps({
  item: Object,
  divider: Boolean,
  truncate: { type: Number, required: false, default: null },
});
</script>
