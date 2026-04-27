<template>
  <MetricsChartsBar
    title="Technologies"
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
const tooltip = (d) =>
  `${d.datum.count} ${d.datum.count === 1 ? "instance" : "instances"}`;

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
