<template>
  <BaseLink
    :autofocus="autofocus"
    :color="color"
    size="large"
    variant="tonal"
    :text="text"
    type="submit"
    block
  />
</template>

<script setup lang="ts">
defineProps({
  text: String,
  autofocus: { type: Boolean, required: false, default: true },
  color: { type: String, required: false, default: "red" },
});
</script>
