<template>
  <MetricsChartsBar
    title="Top Technologies"
    :loading="loading"
    :data="data"
    :series="series"
    :y-label="(item) => item.name"
    :tooltip="tooltip"
    class="w-full"
  />
</template>

<script setup lang="ts">
const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const series = [
  {
    label: "Count",
    color: "var(--color-primary-500)",
    y: (d) => d.count || 0,
  },
];
const total = computed(() =>
  data.value.reduce((sum, d) => sum + (d.count || 0), 0),
);
const tooltip = (d) =>
  metricsTooltip(
    {
      Instances: `${formatCount(d.datum.count)}${metricsPercentage(d.datum.count, total.value)}`,
    },
    d.datum.name,
  );

function fetch() {
  loading.value = true;
  api
    .list(
      "technology/",
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
