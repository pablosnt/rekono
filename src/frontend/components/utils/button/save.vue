<template>
  <v-btn :disabled="disabled" variant="text" hover icon @click="$emit('click')">
    <v-icon icon="mdi-tray-arrow-down" color="green" />
    <v-tooltip activator="parent" text="Save" />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({ disabled: Boolean });
defineEmits(["click"]);
</script>
