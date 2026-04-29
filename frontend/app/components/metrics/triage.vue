<template>
  <div
    class="flex flex-row flex-wrap mt-6 items-start justify-between w-full gap-6"
  >
    <UPageCard
      v-if="loading || hasOpenFindings"
      title="Findings per Triage Status"
      description="Only open findings"
      class="flex-1"
      variant="outline"
    >
      <div v-if="loading" class="flex items-center justify-center">
        <UButton variant="ghost" loading size="xl" />
      </div>
      <VisSingleContainer
        v-else-if="hasOpenFindings"
        :data="treemapData"
        :height="400"
      >
        <VisTreemap
          :value="(d) => d.open"
          :layers="treemapLayers"
          :tile-color="(node) => node.data?.datum?.color"
          :label-internal-nodes="true"
          :tile-padding="8"
          :tile-padding-top="40"
          label-fit="wrap"
          :label-offset-x="15"
          :label-offset-y="15"
          :enable-lightness-variance="true"
        />
        <VisTooltip :triggers="treemapTooltip" />
      </VisSingleContainer>
    </UPageCard>
    <UPageCard
      title="False Positives Rate"
      description="Include all triaged findings, including fixed ones"
      class="flex-1"
      variant="outline"
    >
      <MetricsChartsHalfDonut
        :data="donutData"
        :loading="loading"
        :central-label="`${fpRate.toPrecision(3)}%`"
        :height="400"
        :radius="250"
        :arc-width="50"
        :tooltip="donutTooltip"
      />
    </UPageCard>
  </div>
</template>

<script setup lang="ts">
import { VisSingleContainer, VisTreemap, VisTooltip } from "@unovis/vue";
import { Treemap } from "@unovis/ts";
import { triageStatuses } from "~/constants";

const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const hasOpenFindings = computed(
  () => data.value.filter((d) => d.open > 0).length > 0,
);

const treemapLayers = [(d) => d.triage_status];
const treemapData = computed(() =>
  data.value
    .filter((d) => d.open > 0)
    .map((d) => ({
      ...d,
      color: `var(--color-${triageStatuses.find((s) => s.value === d.triage_status)?.color ?? "neutral"}-500)`,
    })),
);
const totalOpen = computed(() =>
  treemapData.value.reduce((sum, d) => sum + d.open, 0),
);
const treemapTooltip = {
  [Treemap.selectors.tile]: (node) => {
    const d = node.data?.datum;
    if (!d) return null;
    return metricsTooltip(
      {
        Findings: `${formatCount(d.open)}${metricsPercentage(d.open, totalOpen.value)}`,
      },
      d.triage_status,
    );
  },
};

const triaged = computed(() =>
  data.value
    .filter((d) => d.triage_status !== "Untriaged")
    .reduce((sum, d) => sum + d.open + d.fixed, 0),
);
const fps = computed(() => {
  const fp = data.value.find((d) => d.triage_status === "False Positive");
  return fp ? fp.open + fp.fixed : 0;
});
const fpRate = computed(() =>
  triaged.value > 0 ? (fps.value * 100) / triaged.value : 0,
);
const donutTooltip = (d) =>
  metricsTooltip(
    {
      Findings: `${formatCount(d.value)} (${(d.data.label === "false positive"
        ? fpRate.value
        : 100 - fpRate.value
      ).toPrecision(3)}%)`,
    },
    d.data.label === "false positive" ? "False Positives" : "Real Findings",
  );
const donutData = computed(() => [
  {
    label: "false positive",
    value: fps.value,
    color: "var(--color-error-500)",
  },
  {
    label: "real finding",
    value: triaged.value - fps.value,
    color: "var(--color-success-500)",
  },
]);

function fetch() {
  loading.value = true;
  api
    .get(`triaging/${props.project ? `?project=${props.project}` : ""}`)
    .then((response) => (data.value = response))
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>
