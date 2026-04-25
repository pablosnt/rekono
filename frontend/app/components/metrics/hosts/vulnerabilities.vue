<template>
  <UPageCard title="Hosts per Vulnerabilities">
    <div v-if="loading" class="flex items-center justify-center">
      <UButton variant="ghost" loading size="xl" />
    </div>
    <template v-else-if="data.length">
      <VisBulletLegend
        :items="legendItems"
        :on-legend-item-click="onLegendItemClick"
      />
      <div class="overflow-y-auto max-h-500">
        <VisXYContainer :data="data" :height="Math.max(100, data.length * 50)">
          <VisStackedBar
            :x="x"
            :y="activeY"
            :bar-padding="0.2"
            :color="colors"
            orientation="horizontal"
          />
          <VisAxis
            type="x"
            :tick-format="formatCount"
            :tick-values="xTickValues"
          />
          <VisAxis
            type="y"
            :tick-format="hostLabel"
            :tick-values="tickValues"
          />
          <VisTooltip :triggers="tooltipTriggers" />
        </VisXYContainer>
      </div>
    </template>
  </UPageCard>
</template>

<script setup lang="ts">
import {
  VisXYContainer,
  VisStackedBar,
  VisAxis,
  VisTooltip,
  VisBulletLegend,
} from "@unovis/vue";
import { StackedBar } from "@unovis/ts";
import { severities } from "~/constants";

const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const maxCount = computed(() =>
  Math.max(0, ...data.value.map((d) => (d.open || 0) + (d.fixed || 0))),
);
const x = (_, i) => data.value.length - 1 - i;
const hostLabel = (pos: number) => {
  const i = data.value.length - 1 - pos;
  return data.value[i]?.domain || data.value[i]?.ip;
};
const tickValues = computed(() => data.value.map((_, i) => i));
const xTickValues = computed(() =>
  Array.from({ length: maxCount.value + 1 }, (_, i) => i),
);
const reversedSeverities = [...severities].reverse();
const stackLabels = [...reversedSeverities.map((s) => s.value), "Fixed"];
const y = [
  ...reversedSeverities.map((s) => (d) => d[s.value.toLowerCase()]),
  (d) => d.fixed,
];
const colors = [
  ...reversedSeverities.map((s) => {
    let color =
      s.color === "neutral"
        ? "neutral-400"
        : s.color === "info"
          ? "cyan-500"
          : `${s.color}-500`;
    return `var(--color-${color})`;
  }),
  "var(--color-success-500)",
];

const inactive = ref<boolean[]>(stackLabels.map(() => false));

const legendItems = computed(() =>
  stackLabels.map((label, i) => ({
    name: label,
    color: colors[i],
    inactive: inactive.value[i],
  })),
);

const onLegendItemClick = (_: unknown, i: number) => {
  inactive.value = inactive.value.map((v, j) => (j === i ? !v : v));
};

const activeY = computed(() =>
  y.map((accessor, i) => (inactive.value[i] ? null : accessor)),
);

const tooltipTriggers = {
  [StackedBar.selectors.bar]: (d) => {
    const count = Math.round(d.stacked[1] - d.stacked[0]);
    if (count === 0) return "";
    return `${count} ${stackLabels[d.stackIndex]?.toLowerCase()} ${count === 1 ? "vulnerability" : "vulnerabilities"}`;
  },
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
    .then((response) => (data.value = response.items))
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>
