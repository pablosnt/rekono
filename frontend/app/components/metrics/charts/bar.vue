<template>
  <UPageCard :title="title">
    <div v-if="loading" class="flex items-center justify-center">
      <UButton variant="ghost" loading size="xl" />
    </div>
    <template v-else-if="data.length">
      <VisBulletLegend
        v-if="series.length > 1"
        :items="legendItems"
        :on-legend-item-click="onLegendItemClick"
      />
      <div class="overflow-y-auto max-h-500">
        <VisXYContainer
          :data="data"
          :height="Math.max(100, data.length * barHeight)"
        >
          <VisStackedBar
            :x="x"
            :y="activeY"
            :bar-padding="barPadding"
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
            :tick-format="yTickFormat"
            :tick-values="yTickValues"
          />
          <VisTooltip v-if="tooltip" :triggers="tooltipTriggers" />
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
import type { BarSeries } from "~/types/stats";

const props = withDefaults(
  defineProps<{
    title: string;
    loading?: boolean;
    data: Array<unknown>;
    series: BarSeries[];
    yLabel: (item) => string;
    tooltip?: (d) => string | null;
    barHeight?: number;
    barPadding?: number;
  }>(),
  {
    barHeight: 40,
    barPadding: 0.2,
  },
);

const x = (_, i: number) => props.data.length - 1 - i;
const inactive = ref(props.series.map(() => false));
const activeY = computed(() =>
  props.series.map((s, i) => (inactive.value[i] ? null : s.y)),
);
const maxTotal = computed(() =>
  Math.max(
    0,
    ...props.data.map((d) =>
      props.series.reduce((sum, s) => sum + (s.y(d) || 0), 0),
    ),
  ),
);
const xTickValues = computed(() =>
  Array.from({ length: maxTotal.value + 1 }, (_, i) => i),
);
const yTickValues = computed(() => props.data.map((_, i) => i));
const yTickFormat = (pos: number) =>
  props.yLabel(props.data[props.data.length - 1 - pos]);
const colors = computed(() => props.series.map((s) => s.color));
const tooltipTriggers = computed(() => ({
  [StackedBar.selectors.bar]: props.tooltip,
}));
const legendItems = computed(() =>
  props.series.map((s, i) => ({
    name: s.label,
    color: s.color,
    inactive: inactive.value[i] ?? false,
  })),
);

function onLegendItemClick(_, i: number) {
  inactive.value = inactive.value.map((v, j) => (j === i ? !v : v));
}
</script>
