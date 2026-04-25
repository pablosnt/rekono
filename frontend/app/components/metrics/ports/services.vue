<template>
  <UPageCard title="Ports per Service" class="w-full">
    <div v-if="loading" class="flex items-center justify-center">
      <UButton variant="ghost" loading size="xl" />
    </div>
    <VisSingleContainer v-else-if="data.length" :data="data" :height="400">
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
  </UPageCard>
</template>

<script setup lang="ts">
import { VisSingleContainer, VisTreemap, VisTooltip } from "@unovis/vue";
import { Treemap } from "@unovis/ts";

const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const layers = [(d) => d.protocol, (d) => d.service, (d) => d.port];

const tooltipTriggers = {
  [Treemap.selectors.tile]: (node) => {
    const d = node.data?.datum;
    if (!d) return null;
    return `${d.count} ${d.service} ${d.count === 1 ? "service" : "service"} running on port ${d.port}/${d.protocol}`;
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
