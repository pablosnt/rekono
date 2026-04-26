<template>
  <UPageCard title="Technologies per Name" class="w-full">
    <div v-if="loading" class="flex items-center justify-center">
      <UButton variant="ghost" loading size="xl" />
    </div>
    <div v-else-if="data.length" class="overflow-y-auto max-h-500">
      <VisXYContainer :data="data" :height="Math.max(100, data.length * 40)">
        <VisStackedBar
          :x="x"
          :y="[yCount]"
          :color="color"
          orientation="horizontal"
        />
        <VisAxis
          type="x"
          :tick-format="formatCount"
          :tick-values="xTickValues"
        />
        <VisAxis type="y" :tick-format="nameLabel" :tick-values="tickValues" />
        <VisTooltip :triggers="tooltipTriggers" />
      </VisXYContainer>
    </div>
  </UPageCard>
</template>

<script setup lang="ts">
import {
  VisXYContainer,
  VisStackedBar,
  VisAxis,
  VisTooltip,
} from "@unovis/vue";
import { StackedBar } from "@unovis/ts";

const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);

const maxCount = computed(() => Math.max(0, ...data.value.map((d) => d.count)));
const x = (_, i) => data.value.length - 1 - i;
const yCount = (d) => d.count;
const nameLabel = (pos: number) =>
  data.value[data.value.length - 1 - pos]?.name ?? "";
const tickValues = computed(() => data.value.map((_, i) => i));
const xTickValues = computed(() =>
  Array.from({ length: maxCount.value + 1 }, (_, i) => i),
);
const color = "var(--color-primary-500)";

const tooltipTriggers = {
  [StackedBar.selectors.bar]: (d) =>
    `${d.datum.count} ${d.datum.count === 1 ? "instance" : "instances"} of ${d.datum.name}`,
};

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
