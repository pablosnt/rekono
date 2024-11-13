<template>
  <div v-if="tags.length > 0">
    <v-divider v-if="divider" class="mt-3 mb-3" />
    <div class="d-flex justify-center ga-2">
      <v-chip
        v-for="tag in truncate !== null ? tags.slice(0, truncate) : tags"
        :key="tag"
        size="small"
        selected
      >
        {{ tag }}
      </v-chip>
      <p v-if="truncate !== null && truncate < tags.length">...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  tags: Array<string>,
  divider: Boolean,
  truncate: { type: Number, required: false, default: null },
});
</script>
