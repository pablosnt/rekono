<template>
  <BaseButton
    v-if="execution.status === 'Completed' && execution.has_report"
    hover
    icon="mdi-download"
    icon-color="primary"
    tooltip="Download original report"
    @click="api.download(execution.id, 'report/', {})"
  />
</template>

<script setup lang="ts">
defineProps({ api: Object, execution: Object });
</script>
