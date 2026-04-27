<template>
  <div class="flex flex-col flex-wrap mt-6 space-y-6">
    <div class="flex flex-row flex-wrap items-start justify-between w-full">
      <FindingsCounterSingle
        class="w-60 h-40"
        :project-id="project"
        finding-name-plural="Vulnerabilities"
      />
      <MetricsVulnerabilitiesSeverity :project="project" class="flex-1 ml-6" />
    </div>
    <div
      class="flex flex-row flex-wrap items-start justify-between w-full gap-6"
    >
      <MetricsVulnerabilitiesCve :project="project" class="flex-1" />
      <MetricsVulnerabilitiesCwe :project="project" class="flex-1" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ project?: string | number }>();
</script>
