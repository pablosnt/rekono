<template>
  <UPageCard :title="title" :ui="{ container: 'min-w-0' }">
    <USkeleton v-if="loading" class="h-64 w-full rounded-lg" />
    <template v-else-if="data.length">
      <VisBulletLegend
        v-if="series.length > 1"
        :items="legendItems"
        :on-legend-item-click="onLegendItemClick"
      />
      <div :class="isVertical ? 'overflow-x-auto' : 'overflow-y-auto'">
        <VisXYContainer
          :data="data"
          :height="
            isVertical
              ? barHeight
              : Math.min(500, Math.max(200, data.length * barHeight))
          "
        >
          <VisStackedBar
            :x="x"
            :y="activeY"
            :bar-padding="barPadding"
            :color="colors"
            :cursor="onBarClick ? 'pointer' : undefined"
            :events="barEvents"
            :orientation="orientation"
          />
          <VisAxis
            :type="isVertical ? 'x' : 'y'"
            :tick-format="categoryTickFormat"
            :tick-values="categoryTickValues"
          />
          <VisAxis
            :type="isVertical ? 'y' : 'x'"
            :tick-format="formatCount"
            :tick-values="countTickValues"
          />
          <VisTooltip v-if="tooltip" :triggers="tooltipTriggers" />
        </VisXYContainer>
      </div>
    </template>
    <MetricsChartsEmpty v-else />
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
    onBarClick?: (d) => void;
    orientation?: "horizontal" | "vertical";
    barHeight?: number;
    barPadding?: number;
  }>(),
  {
    orientation: "horizontal",
    barHeight: 40,
    barPadding: 0.2,
  },
);

const isVertical = computed(() => props.orientation === "vertical");
const x = computed(() =>
  isVertical.value
    ? (_, i: number) => i
    : (_, i: number) => props.data.length - 1 - i,
);
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
const countTickValues = computed(() =>
  Array.from({ length: maxTotal.value + 1 }, (_, i) => i),
);
const categoryTickValues = computed(() => props.data.map((_, i) => i));
const categoryTickFormat = (pos: number) =>
  isVertical.value
    ? props.yLabel(props.data[pos])
    : props.yLabel(props.data[props.data.length - 1 - pos]);
const colors = computed(() =>
  props.series.some((s) => typeof s.color === "function")
    ? (d: unknown, stackIndex: number) => {
        const s = props.series[stackIndex];
        return typeof s?.color === "function" ? s.color(d) : (s?.color ?? null);
      }
    : props.series.map((s) => s.color as string),
);
const barEvents = computed(() =>
  props.onBarClick
    ? {
        [StackedBar.selectors.bar]: {
          click: (d: { datum: unknown }) => props.onBarClick!(d.datum),
        },
      }
    : undefined,
);
const tooltipTriggers = computed(() => ({
  [StackedBar.selectors.bar]: props.tooltip,
}));
const legendItems = computed(() =>
  props.series.map((s, i) => ({
    name: s.label,
    color: s.legendColor ?? (typeof s.color === "string" ? s.color : null),
    inactive: inactive.value[i] ?? false,
  })),
);

function onLegendItemClick(_, i: number) {
  inactive.value = inactive.value.map((v, j) => (j === i ? !v : v));
}
</script>
