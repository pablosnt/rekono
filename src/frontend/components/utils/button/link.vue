<template>
  <v-btn
    v-if="link"
    variant="text"
    :icon="icon"
    color="medium-emphasis"
    :target="target"
    :href="link"
    hover
  />
</template>

<script setup lang="ts">
defineProps({
  link: String,
  icon: { type: String, required: false, default: "mdi-open-in-new" },
  target: { type: String, required: false, default: "_blank" },
});
</script>
