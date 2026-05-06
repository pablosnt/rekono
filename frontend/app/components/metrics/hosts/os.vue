<template>
  <UPageCard
    title="Operative Systems"
    class="w-full"
    variant="outline"
    :ui="{ container: 'min-w-0' }"
  >
    <div v-if="loading" class="flex items-center justify-center">
      <UButton variant="ghost" loading size="xl" />
    </div>
    <template v-else-if="data.length">
      <VisBulletLegend
        :items="legendItems"
        :on-legend-item-click="onLegendItemClick"
      />
      <VisSingleContainer :data="activeData" :height="200" class="flex-none">
        <VisDonut
          :value="(d) => d.count"
          :color="(d) => d.color"
          :arc-width="25"
        />
        <VisTooltip :triggers="tooltipTriggers" />
      </VisSingleContainer>
    </template>
  </UPageCard>
</template>

<script setup lang="ts">
import {
  VisSingleContainer,
  VisDonut,
  VisTooltip,
  VisBulletLegend,
} from "@unovis/vue";
import { Donut } from "@unovis/ts";
import { hostOS } from "~/constants";

const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const total = ref(0);
const inactive = ref<boolean[]>([]);

const legendItems = computed(() =>
  data.value.map((d, i) => ({
    name: d.os_type,
    color: d.color,
    inactive: inactive.value[i],
  })),
);

const onLegendItemClick = (_: unknown, i: number) => {
  inactive.value = inactive.value.map((v, j) => (j === i ? !v : v));
};

const activeData = computed(() =>
  data.value.filter((_, i) => !inactive.value[i]),
);

const tooltipTriggers = {
  [Donut.selectors.segment]: (d) =>
    metricsTooltip(
      {
        Hosts: `${formatCount(d.value)}${metricsPercentage(d.value, total.value)}`,
      },
      d.data.os_type,
    ),
};

function fetch() {
  loading.value = true;
  api
    .get(`host-os/${props.project ? `?project=${props.project}` : ""}`)
    .then((response) => {
      data.value = response.map((item) => {
        return {
          os_type: item.os_type,
          count: item.count,
          color: `var(--color-${hostOS.find((o) => o.value === item.os_type)?.color ?? "neutral"}-500)`,
        };
      });
      total.value = response.reduce((sum, d) => sum + d.count, 0);
      inactive.value = data.value.map(() => false);
    })
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>
