<template>
  <UTooltip
    :text="ok ? 'Available' : 'Not available. Change connection settings'"
    :content="{ side: 'left', sideOffset: 8, collisionPadding: 8 }"
  >
    <UButton
      :color="ok ? 'success' : 'error'"
      variant="ghost"
      :loading="loading"
      :icon="ok ? 'i-lucide-check' : 'i-lucide-unplug'"
      :aria-label="ok ? 'Available' : 'Not available'"
    />
  </UTooltip>
</template>

<script setup lang="ts">
defineProps<{
  ok?: boolean;
  loading?: boolean;
}>();
</script>
