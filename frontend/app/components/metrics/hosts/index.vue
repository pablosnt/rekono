<template>
  <div class="flex flex-col flex-wrap mt-6 space-y-6">
    <div class="flex flex-row flex-wrap items-start justify-between w-full">
      <FindingsCounterSingle
        class="w-60 h-40"
        :project-id="project"
        finding-name-plural="Hosts"
      />
      <MetricsHostsOs :project="project" class="flex-1 ml-6" />
    </div>
    <MetricsHostsLocations :project="project" />
    <MetricsHostsVulnerabilities :project="project" />
  </div>
</template>

<script setup lang="ts">
defineProps<{ project?: string | number }>();
</script>
