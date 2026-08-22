<template>
  <TasksButton
    size="lg"
    not-rounded
    :label="hasScans ? 'Run Scan' : 'Run First Scan'"
  />
</template>

<script setup lang="ts">
defineProps<{ hasScans?: boolean }>();
</script>
