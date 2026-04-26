<template>
  <div class="space-y-8">
    <MetricsEvolution :project="$route.params.project_id" />
    <UTabs :items="tabs" class="w-full">
      <template #hosts>
        <MetricsHosts :project="$route.params.project_id" />
      </template>
      <template #ports>
        <MetricsPorts :project="$route.params.project_id" />
      </template>
      <template #technologies>
        <MetricsTechnologies :project="$route.params.project_id" />
      </template>
    </UTabs>
  </div>
</template>

<script setup lang="ts">
const tabs = [
  { label: "Hosts", slot: "hosts", icon: "i-lucide-server" },
  { label: "Ports", slot: "ports", icon: "i-lucide-ethernet-port" },
  { label: "Technologies", slot: "technologies", icon: "i-lucide-layers" },
  { label: "Vulnerabilities", slot: "vulnerabilities", icon: "i-lucide-bug" },
  { label: "Exploits", slot: "exploits", icon: "i-lucide-flame" },
  { label: "Others", slot: "others", icon: "i-lucide-scan" },
  { label: "Triage", slot: "triage", icon: "i-lucide-shield-check" },
];
// TODO: Is it possible to get the number of findings from the parent panel? They already have the values for showing them in the panel
// TODO: If no findings, empty message
// TODO: Filter the tabs if no items from a given finding type
</script>
