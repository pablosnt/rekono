<template>
  <div v-if="loading" class="flex items-center justify-center">
    <UButton variant="ghost" loading size="xl" />
  </div>
  <VisSingleContainer v-else-if="hasValues" :data="data" :height="height">
    <VisDonut
      :value="(d) => d.value"
      :color="(d) => d.color"
      :central-label="centralLabel"
      :central-label-offset-y="-20"
      :angle-range="DONUT_HALF_ANGLE_RANGE_TOP"
      :radius="radius"
      :corner-radius="3"
      :arc-width="arcWidth"
      :pad-angle="0.01"
    />
    <VisTooltip v-if="tooltip" :triggers="tooltipTriggers" />
  </VisSingleContainer>
</template>

<script setup lang="ts">
import { VisSingleContainer, VisDonut, VisTooltip } from "@unovis/vue";
import { Donut, DONUT_HALF_ANGLE_RANGE_TOP } from "@unovis/ts";

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
    arcWidth: 32,
  },
);

const hasValues = computed(() => props.data.some((d) => d.value > 0));
const tooltipTriggers = computed(() => ({
  [Donut.selectors.segment]: props.tooltip,
}));
</script>
