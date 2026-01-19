<template>
  <UTooltip
    :text="ok ? 'Available' : 'Not available. Change connection settings'"
  >
    <UButton
      :color="ok ? 'success' : 'error'"
      variant="ghost"
      :loading="loading"
      :icon="ok ? 'i-lucide-check' : 'i-lucide-unplug'"
    />
  </UTooltip>
</template>

<script setup lang="ts">
defineProps<{
  ok?: boolean;
  loading?: boolean;
}>();
</script>
