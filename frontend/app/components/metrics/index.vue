<template>
  <div class="space-y-8">
    <!-- TODO: Page title Metrics -->
    <!-- TODO: Add Findings Evolution as title -->
    <MetricsEvolution :project="$route.params.project_id" />
    <UTabs v-model="tab" :items="tabs" class="w-full">
      <template #content="{ item }">{{ item.label }}<br />{{ tab }}</template>
    </UTabs>
  </div>
</template>

<script setup lang="ts">
const tab = ref("0");
const tabs = [
  { label: "Hosts", icon: "i-lucide-server" },
  { label: "Ports", icon: "i-lucide-ethernet-port" },
  { label: "Technologies", icon: "i-lucide-layers" },
  { label: "Vulnerabilities", icon: "i-lucide-bug" },
  { label: "Exploits", icon: "i-lucide-flame" },
  { label: "Others", icon: "i-lucide-scan" },
  { label: "Triage", icon: "i-lucide-shield-check" },
];
// TODO: When a metrics tab is selected, the line corresponding to that finding type must be bigger
// TODO: If no findings, empty message
// TODO: Add links from the counters of each section to each finding page
</script>
