<template>
  <v-btn
    v-if="execution.status === 'Completed' && execution.has_report"
    hover
    variant="text"
    icon
    @click="api.download(execution.id, 'report/', {})"
  >
    <v-icon icon="mdi-download" color="primary" />
    <v-tooltip activator="parent" text="Download original report" />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({ api: Object, execution: Object });
</script>
