<template>
  <v-btn
    v-if="link"
    variant="text"
    icon
    :color="color"
    :target="sameTab ? '_self' : '_blank'"
    :href="link"
    :size="size"
    hover
  >
    <v-icon :icon="icon" />
    <v-tooltip
      v-if="tooltip !== undefined"
      activator="parent"
      :text="tooltip"
    />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({
  link: String,
  icon: { type: String, required: false, default: "mdi-open-in-new" },
  sameTab: { type: Boolean, required: false, default: false },
  size: { type: String, required: false, default: undefined },
  color: { type: String, required: false, default: "medium-emphasis" },
  tooltip: { type: String, required: false, default: undefined },
});
</script>
