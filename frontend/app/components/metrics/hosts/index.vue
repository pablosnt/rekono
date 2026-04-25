<template>
  <div class="flex flex-col flex-wrap mt-6 space-y-6">
    <div class="flex flex-row flex-wra items-start justify-around w-full">
      <FindingsCounterSingle
        class="w-60 h-40"
        :project-id="project"
        finding-name-plural="Hosts"
      />
      <MetricsHostsOs :project="project" />
    </div>
    <MetricsHostsVulnerabilities :project="project" />
  </div>
</template>

<script setup lang="ts">
defineProps<{ project?: string | number }>();
</script>
