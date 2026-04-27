<template>
  <MetricsChartsBar
    title="CWEs"
    :loading="loading"
    :data="data"
    :series="series"
    :y-label="(item) => item.cwe"
    :tooltip="tooltip"
    class="w-full"
  />
</template>

<script setup lang="ts">
import type { BarSeries } from "~/types/stats";

const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const series: BarSeries[] = [
  {
    label: "Open",
    color: "var(--color-primary-500)",
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
  return `${count} ${series[d.stackIndex]?.label.toLowerCase()} ${count === 1 ? "vulnerability" : "vulnerabilities"}`;
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
