<template>
  <div class="flex flex-col mt-6 space-y-6">
    <div class="flex flex-col sm:flex-row gap-6 items-start">
      <FindingsCounterSingle
        class="w-full sm:w-60 h-40 shrink-0"
        :project-id="project"
        finding-name-plural="Hosts"
        only-active
      />
      <MetricsHostsOs :project="project" class="w-full sm:flex-1 min-w-0" />
    </div>
    <MetricsHostsLocations :project="project" />
    <MetricsHostsVulnerabilities :project="project" />
  </div>
</template>

<script setup lang="ts">
defineProps<{ project?: number }>();
</script>
