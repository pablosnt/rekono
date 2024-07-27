<template>
  <v-divider v-if="divider && item.tags.length > 0" class="mt-3 mb-3" />
  <v-chip-group v-if="item.tags.length > 0" selected-class="v-chip">
    <v-chip v-for="tag in item.tags" :key="tag" size="small">
      {{ tag }}
    </v-chip>
  </v-chip-group>
</template>

<script setup lang="ts">
defineProps({ item: Object, divider: Boolean });
</script>
