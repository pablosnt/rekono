<template>
  <UPageCard title="Hosts per OS" class="w-200" variant="outline">
    <div v-if="loading" class="flex items-center justify-center">
      <UButton variant="ghost" loading  size="xl" />
    </div>
    <VisSingleContainer
      v-else-if="data.length"
      :data="data"
      :height="200"
      class="flex-none"
    >
      <VisDonut
        :value="(d) => d.count"
        :color="(d) => d.color"
        :arc-width="25"
      />
      <VisTooltip :triggers="tooltipTriggers" />
    </VisSingleContainer>
  </UPageCard>
</template>

<script setup lang="ts">
import { VisSingleContainer, VisDonut, VisTooltip } from "@unovis/vue";
import { Donut } from "@unovis/ts";
import { hostOS } from "~/constants";

const props = defineProps<{ project?: string | number }>();

const api = useApi("/api/stats/");
const loading = ref(true);
const data = ref([]);
const total = ref(0);

const tooltipTriggers = {
  [Donut.selectors.segment]: (d) =>
    `<b>${d.data.os_type}</b>: ${d.value} ${d.value === 1 ? "host" : "hosts"}`,
};

function fetch() {
  loading.value = true;
  api
    .get(`host-os/${props.project ? `?project=${props.project}` : ""}`)
    .then((response) => {
      data.value = response.map((item) => {
        const os = hostOS.find((o) => o.value === item.os_type);
        return {
          os_type: item.os_type,
          count: item.count,
          icon: os?.icon ?? "i-lucide-server",
          color: `var(--color-${os?.color ?? "neutral"}-500)`,
        };
      });
      total.value = response.reduce((sum, d) => sum + d.count, 0);
    })
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>
