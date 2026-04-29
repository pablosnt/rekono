<template>
  <MetricsChartsBar
    title="Most Vulnerable Hosts"
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
  const label = series[d.stackIndex]?.label;
  const host = d.datum.domain || d.datum.ip;
  return label === "Fixed"
    ? metricsTooltip(
        {
          "Fixed Vulnerabilities": `${formatCount(count)}${metricsPercentage(count, d.datum.totalOpen + (d.datum.fixed || 0))}`,
          "Open Vulnerabilities": d.datum.totalOpen,
        },
        host,
      )
    : metricsTooltip(
        {
          [`${label} Vulnerabilities`]: `${formatCount(count)}${metricsPercentage(count, d.datum.totalOpen)}`,
          "Open Vulnerabilities": d.datum.totalOpen,
        },
        host,
      );
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
    .then((response) => {
      data.value = response.items.map((item) => ({
        ...item,
        totalOpen: reversedSeverities.reduce(
          (sum, s) => sum + (item[s.value.toLowerCase()] || 0),
          0,
        ),
      }));
    })
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>
