<template>
  <v-btn
    :disabled="report.status !== 'Ready'"
    hover
    variant="text"
    icon
    @click="api.download(report.id, 'download/', {})"
  >
    <v-icon icon="mdi-download" color="primary" />
    <v-tooltip activator="parent" text="Download" />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({ api: Object, report: Object });
</script>
