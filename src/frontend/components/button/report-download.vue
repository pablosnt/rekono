<template>
  <v-btn
    :disabled="report.status !== 'Ready'"
    hover
    variant="text"
    icon
    @click="api.get(report.id, 'download/', {}, true)"
  >
    <v-icon icon="mdi-download" color="primary" />
    <v-tooltip activator="parent" text="Download" />
  </v-btn>
</template>
<!-- TODO: Download files automatically -->
<script setup lang="ts">
defineProps({ api: Object, report: Object });
</script>
