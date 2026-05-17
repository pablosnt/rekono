<template>
  <UButton
    label="Explore Projects"
    icon="i-lucide-folder"
    size="lg"
    to="/projects"
    :variant="variant"
    :color="color"
  />
</template>

<script setup lang="ts">
defineProps<{
  variant?: string;
  color?: string;
}>();
</script>
