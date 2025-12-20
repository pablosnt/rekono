<template>
  <div class="flex flex-wrap gap-1">
    <UBadge
      v-for="tag in tags?.slice(0, 5) || []"
      :key="tag"
      :label="tag"
      color="neutral"
      variant="subtle"
      size="xs"
    />
    <span v-if="tags && tags.length > 5" class="text-xs text-muted-foreground">
      +{{ tags.length - 5 }}
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ tags: string[] }>();
</script>
