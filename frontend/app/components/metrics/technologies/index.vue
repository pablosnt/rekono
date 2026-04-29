<template>
  <div class="flex flex-row flex-wrap mt-6 items-start justify-around w-full">
    <FindingsCounterSingle
      class="w-60 h-40"
      :project-id="project"
      finding-name-plural="Technologies"
      only-active
    />
    <MetricsTechnologiesNames :project="project" class="flex-1 ml-6" />
  </div>
</template>

<script setup lang="ts">
defineProps<{ project?: string | number }>();
</script>
