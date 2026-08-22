<template>
  <div class="flex gap-1">
    <UBadge
      v-for="tag in visibleTags"
      :key="tag"
      :label="tag"
      color="neutral"
      variant="subtle"
    />
    <span
      v-if="props.tags && props.tags.length > 5"
      class="text-muted-foreground"
    >
      +{{ props.tags.length - 5 }}
    </span>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ tags: string[] }>();
const visibleTags = computed(() => props.tags?.slice(0, 5) || []);
</script>
