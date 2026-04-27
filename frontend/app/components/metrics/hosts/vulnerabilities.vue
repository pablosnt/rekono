<template>
  <MetricsChartsBar
    title="Hosts per Vulnerabilities"
    :loading="loading"
    :data="data"
    :series="series"
    :y-label="(item) => item.domain || item.ip"
    :tooltip="tooltip"
    class="w-full"
  />
</template>

<script setup lang="ts">
import { severities } from "~/constants";

const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const reversedSeverities = [...severities].reverse();
const stackLabels = [...reversedSeverities.map((s) => s.value), "Fixed"];
const series = [
  ...reversedSeverities.map((s) => ({
    label: s.value,
    color: `var(--color-${s.color === "info" ? "cyan-500" : `${s.color}-500`})`,
    y: (d) => d[s.value.toLowerCase()] || 0,
  })),
  {
    label: "Fixed",
    color: "var(--color-success-500)",
    y: (d) => d.fixed || 0,
  },
];
const tooltip = (d) => {
  const count = Math.round(d.stacked[1] - d.stacked[0]);
  const label = stackLabels[d.stackIndex]?.toLowerCase();
  return `${count} ${label === "fixed" ? label : `open ${label}`} ${count === 1 ? "vulnerability" : "vulnerabilities"}`;
};

function fetch() {
  loading.value = true;
  api
    .list(
      "host-vulnerabilities/",
      props.project ? { project: props.project } : {},
      false,
      1,
      100,
    )
    .then((response) => (data.value = response.items))
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>
