<template>
  <div class="flex flex-col flex-wrap mt-6 space-y-6">
    <div class="flex flex-row items-start justify-around w-full">
      <FindingsCounterSingle
        class="w-60 h-40"
        :project-id="project"
        finding-name-plural="Technologies"
      />
      <MetricsTechnologiesNames :project="project" class="flex-1 ml-6" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ project?: string | number }>();
</script>
