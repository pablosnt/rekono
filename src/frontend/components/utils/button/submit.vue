<template>
  <v-btn
    :autofocus="autofocus"
    :color="color"
    size="large"
    variant="tonal"
    :text="text"
    type="submit"
    :disabled="disabled"
    :prepend-icon="prependIcon"
    block
  />
</template>

<script setup lang="ts">
defineProps({
  text: String,
  autofocus: { type: Boolean, required: false, default: true },
  disabled: { type: Boolean, required: false, default: false },
  color: { type: String, required: false, default: "red" },
  prependIcon: { type: String, required: false, default: undefined },
});
// CODE: Remove this component and use the v-btn directly or BaseLink
</script>
