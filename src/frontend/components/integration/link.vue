<template>
  <v-btn
    variant="text"
    target="_blank"
    :href="link ? link : integration.reference"
    @click.stop
  >
    <v-avatar size="small" :image="integration.icon" />
    <v-tooltip
      v-if="tooltip"
      activator="parent"
      :text="tooltipText ? tooltipText : integration.name"
    />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({
  integration: Object,
  link: { type: String, required: false, default: null },
  tooltip: { type: Boolean, required: false, default: false },
  tooltipText: { type: String, required: false, default: null },
});
</script>
