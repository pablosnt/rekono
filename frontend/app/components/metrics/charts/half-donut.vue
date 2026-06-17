<template>
  <div ref="containerRef">
    <USkeleton v-if="loading" class="h-[180px] w-full rounded-lg" />
    <VisSingleContainer
      v-else-if="hasValues"
      :data="data"
      :height="effectiveHeight"
    >
      <VisDonut
        :value="(d) => d.value"
        :color="(d) => d.color"
        :central-label="centralLabel"
        :central-label-offset-y="-20"
        :angle-range="DONUT_HALF_ANGLE_RANGE_TOP"
        :radius="effectiveRadius"
        :corner-radius="3"
        :arc-width="arcWidth"
        :pad-angle="0.01"
      />
      <VisTooltip v-if="tooltip" :triggers="tooltipTriggers" />
    </VisSingleContainer>
  </div>
</template>

<script setup lang="ts">
import { VisSingleContainer, VisDonut, VisTooltip } from "@unovis/vue";
import { Donut, DONUT_HALF_ANGLE_RANGE_TOP } from "@unovis/ts";
import { useElementSize } from "@vueuse/core";

const props = withDefaults(
  defineProps<{
    data: Array<{ value: number; color: string; [key: string]: unknown }>;
    loading?: boolean;
    centralLabel?: string;
    radius?: number;
    arcWidth?: number;
    height?: number;
    tooltip?: (d: unknown) => string;
  }>(),
  {
    loading: false,
    radius: 160,
    arcWidth: 35,
  },
);

const containerRef = ref<HTMLElement | null>(null);
const { width: containerWidth } = useElementSize(containerRef);
const effectiveRadius = computed(() => {
  if (containerWidth.value <= 0) return props.radius;
  return Math.min(
    props.radius,
    (containerWidth.value - props.arcWidth * 2) / 2,
  );
});
const effectiveHeight = computed(() =>
  props.height === undefined
    ? undefined
    : Math.min(props.height, effectiveRadius.value + props.arcWidth * 2),
);
const hasValues = computed(() => props.data.some((d) => d.value > 0));
const tooltipTriggers = computed(() => ({
  [Donut.selectors.segment]: props.tooltip,
}));
</script>
