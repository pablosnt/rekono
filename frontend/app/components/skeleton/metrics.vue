<template>
  <div>
    <div
      v-if="title || legend > 0"
      class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"
    >
      <USkeleton v-if="title" class="h-8 w-56" />
      <div v-if="legend > 0" class="flex flex-wrap gap-3">
        <USkeleton v-for="item in legend" :key="item" class="h-4 w-20" />
      </div>
    </div>
    <USkeleton class="w-full rounded-lg" :style="{ height: `${height}px` }" />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{ height?: number; title?: boolean; legend?: number }>(),
  { height: 400, legend: 0 },
);
</script>
