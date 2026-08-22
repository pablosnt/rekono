<template>
  <UPageCard
    :title="title"
    :description="description"
    :variant="variant"
    :ui="{ container: 'min-w-0' }"
  >
    <SkeletonMetrics
      v-if="loading"
      :height="skeletonHeight"
      :legend="skeletonLegend"
    />
    <slot v-else-if="hasData" />
    <UEmpty
      v-else
      icon="i-lucide-chart-bar"
      title="No data available"
      variant="naked"
    />
  </UPageCard>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string;
    description?: string;
    variant?: string;
    loading?: boolean;
    hasData?: boolean;
    skeletonHeight?: number;
    skeletonLegend?: number;
  }>(),
  { variant: "outline", skeletonHeight: 400, skeletonLegend: 0 },
);
</script>
