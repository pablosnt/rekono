<template>
  <v-container v-if="tags.length > 0" fluid>
    <v-row justify="center" dense>
      <v-divider v-if="divider" class="mt-3 mb-3" />
      <v-chip-group class="justify-center" multiple @click.prevent.stop>
        <v-chip
          v-for="tag in truncate !== null ? tags.slice(0, truncate) : tags"
          :key="tag"
          :text="tag"
        />
      </v-chip-group>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
defineProps({
  tags: Array<string>,
  divider: Boolean,
  truncate: { type: Number, required: false, default: null },
});
</script>
