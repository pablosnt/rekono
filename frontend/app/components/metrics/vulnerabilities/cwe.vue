<template>
  <MetricsChartsBar
    title="Top CWEs"
    :loading="loading"
    :data="data"
    :series="series"
    :y-label="(item) => item.cwe"
    :tooltip="tooltip"
    :on-bar-click="
      (d) =>
        d.cwe
          ? navigateTo(
              `https://cwe.mitre.org/data/definitions/${d.cwe.toUpperCase().replace('CWE-', '')}.html`,
              { external: true, open: { target: '_blank' } },
            )
          : null
    "
    class="w-full"
  />
</template>

<script setup lang="ts">
import type { BarSeries } from "~/types/stats";

const props = defineProps<{ project?: number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const series: BarSeries[] = [
  {
    label: "Open",
    color: "var(--ui-primary)",
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
    d.datum.cwe,
  );
};

function fetch() {
  loading.value = true;
  api
    .list(
      "vulnerability-cwe/",
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
