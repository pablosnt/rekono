<template>
  <div class="pt-6 space-y-8">
    <div class="flex flex-wrap items-start gap-6 w-full justify-around">
      <div class="flex-1">
        <FindingsCounterSingle
        :project-id="project"
        finding-name-plural="Hosts"
      />
      </div>
      <div class="flex-1">
        <MetricsHostsOs :project="project" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ project?: string | number }>();
</script>
