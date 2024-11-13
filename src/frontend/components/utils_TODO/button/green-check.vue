<template>
  <v-btn hover icon variant="text">
    <v-icon
      :icon="condition ? 'mdi-check-circle' : 'mdi-close-circle'"
      :color="condition ? 'green' : 'red'"
    />
    <v-tooltip activator="parent" :text="condition ? trueText : falseText" />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({
  condition: Boolean,
  trueText: String,
  falseText: String,
});
</script>
