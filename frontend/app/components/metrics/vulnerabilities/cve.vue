<template>
  <MetricsChartsBar
    title="Top CVEs"
    :loading="loading"
    :data="data"
    :series="series"
    :y-label="(item) => item.cve"
    :tooltip="tooltip"
    :on-bar-click="
      (d) =>
        d.link
          ? navigateTo(d.link, { external: true, open: { target: '_blank' } })
          : null
    "
    class="w-full"
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
      `var(--color-${severities.find((s) => s.value === d.severity_value)?.color || "primary"}-500)`,
    legendColor: "var(--color-primary-500)",
    y: (d) => d.open,
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
      Severity: d.datum.severity_value,
      Status: series[d.stackIndex]?.label,
      Vulnerabilities: `${formatCount(count)}${metricsPercentage(count, (d.datum.open || 0) + (d.datum.fixed || 0))}`,
    },
    d.datum.cve,
  );
};

function fetch() {
  loading.value = true;
  api
    .list(
      "vulnerability-cve/",
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
