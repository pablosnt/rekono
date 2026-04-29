<template>
  <MetricsChartsBar
    title="Vulnerabilities per Severity"
    :loading="loading"
    :data="data"
    :series="series"
    :y-label="(item) => item.severity"
    :tooltip="tooltip"
    orientation="vertical"
    :bar-height="400"
  />
</template>

<script setup lang="ts">
import { severities } from "~/constants";
import type { BarSeries } from "~/types/stats";

const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const series: BarSeries[] = [
  {
    label: "Open",
    color: (d) =>
      `var(--color-${severities.find((s) => s.value === d.severity)?.color || "primary"}-500)`,
    legendColor: "var(--color-primary-500)",
    y: (d) => d.open || 0,
  },
  {
    label: "Fixed",
    color: "var(--color-success-500)",
    y: (d) => d.fixed || 0,
  },
];
const tooltip = (d) => {
  const count = Math.round(d.stacked[1] - d.stacked[0]);
  return metricsTooltip(
    {
      Status: series[d.stackIndex]?.label,
      Vulnerabilities: `${formatCount(count)}${metricsPercentage(count, (d.datum.open || 0) + (d.datum.fixed || 0))}`,
    },
    d.datum.severity,
  );
};

function fetch() {
  loading.value = true;
  api
    .get(
      `vulnerability-status/${props.project ? `?project=${props.project}` : ""}`,
    )
    .then((response) => (data.value = response))
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>
