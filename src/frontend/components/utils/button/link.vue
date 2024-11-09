<template>
  <!-- CODE: Review from where is this used, and consider hardcode the button. Review also all the occurrences of links via href to Rekono endpoints -->
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
  target: { type: String, required: false, default: "_blank" },
  size: { type: String, required: false, default: undefined },
  color: { type: String, required: false, default: "medium-emphasis" },
  tooltip: { type: String, required: false, default: undefined },
});
</script>
