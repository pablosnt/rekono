<template>
  <UModal
    :title="title"
    :description="description"
    :open="open"
    :ui="{ content: 'sm:max-w-3xl sm:max-h-xl' }"
    @update:open="(value) => $emit('open', value)"
  >
    <template #body>
      <slot />
    </template>
  </UModal>
</template>

<script setup lang="ts">
defineProps<{
  open: boolean;
  title?: string;
  description?: string;
}>();
defineEmits<{ open: [open: boolean] }>();
</script>
