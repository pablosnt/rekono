<template>
  <BaseButton
    hover
    :icon="condition ? 'mdi-check-circle' : 'mdi-close-circle'"
    :icon-color="condition ? 'green' : 'red'"
    :tooltip="condition ? trueText : falseText"
  />
</template>

<script setup lang="ts">
defineProps({
  condition: Boolean,
  trueText: String,
  falseText: String,
});
</script>
