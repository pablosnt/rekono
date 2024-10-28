<template>
  <v-btn
    v-if="link"
    variant="text"
    icon
    :color="color"
    :target="target"
    :href="link"
    :size="size"
    hover
  >
    <v-icon :icon="icon" />
    <v-tooltip v-if="tooltip" :text="tooltip" />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({
  link: String,
  icon: { type: String, required: false, default: "mdi-open-in-new" },
  target: { type: String, required: false, default: "_blank" },
  size: { type: String, required: false, default: undefined },
  color: { type: String, required: false, default: "medium-emphasis" },
  tooltip: { type: String, required: false, default: undefined },
});
</script>
