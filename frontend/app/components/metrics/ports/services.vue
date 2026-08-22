<template>
  <MetricsCard
    title="Top Ports & Services"
    class="w-full"
    :loading="loading"
    :has-data="data.length > 0"
  >
    <VisSingleContainer :data="data" :height="400">
      <VisTreemap
        :value="(d) => d.count"
        :layers="layers"
        :label-internal-nodes="true"
        :tile-padding="8"
        :tile-padding-top="40"
        label-fit="wrap"
        :label-offset-x="15"
        :label-offset-y="15"
        :enable-lightness-variance="true"
      />
      <VisTooltip :triggers="tooltipTriggers" />
    </VisSingleContainer>
  </MetricsCard>
</template>

<script setup lang="ts">
import { VisSingleContainer, VisTreemap, VisTooltip } from "@unovis/vue";
import { Treemap } from "@unovis/ts";

const props = defineProps<{ project?: number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const layers = [(d) => d.protocol, (d) => d.service, (d) => d.port];
const total = computed(() =>
  data.value.reduce((sum, d) => sum + (d.count || 0), 0),
);

const tooltipTriggers = {
  [Treemap.selectors.tile]: (node) => {
    const d = node.data?.datum;
    if (!d) return null;
    return metricsTooltip({
      Service: d.service,
      Port: d.port,
      Protocol: d.protocol.toUpperCase(),
      Instances: `${formatCount(d.count)}${metricsPercentage(d.count, total.value)}`,
    });
  },
};

function fetch() {
  loading.value = true;
  api
    .list(
      "port/",
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
