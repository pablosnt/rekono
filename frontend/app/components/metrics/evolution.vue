<template>
  <div
    class="flex flex-col flex-wrap sm:flex-row sm:items-center sm:justify-between gap-2 mb-5"
  >
    <h2 class="text-2xl font-bold text-default">Findings Evolution</h2>
    <VisBulletLegend
      :items="legendItems"
      :on-legend-item-click="onLegendItemClick"
    />
  </div>
  <div
    ref="container"
    class="overflow-x-auto"
    :class="{ 'min-h-[500px]': loading }"
  >
    <UProgress v-if="loading" />
    <VisXYContainer
      v-else-if="data.length"
      :data="data"
      :height="500"
      :width="data.length > 12 ? data.length * 80 : undefined"
    >
      <VisLine :x="x" :y="activeY" :color="colors" />
      <VisAxis type="x" :tick-format="formatMonth" :tick-values="tickValues" />
      <VisAxis
        type="y"
        :num-ticks="4"
        :tick-format="formatCount"
        :grid-line="false"
      />
      <VisCrosshair :color="colors" :template="tooltip" />
      <VisTooltip />
    </VisXYContainer>
  </div>
</template>

<script setup lang="ts">
import {
  VisXYContainer,
  VisLine,
  VisAxis,
  VisCrosshair,
  VisTooltip,
  VisBulletLegend,
} from "@unovis/vue";
import { findingTypes } from "~/constants";
import type { FindingsEvolution } from "~/types/stats";

const props = defineProps<{ project?: number }>();
const api = useApi("/api/stats/");
const loading = ref(true);
const container = ref<HTMLElement>();
const stats = ref<Record<string, FindingsEvolution[]>>({});
const data = computed(() => processStats());
const x = (d) => new Date(d.month).getTime();
const y = findingTypes.map(
  (ft) => (d) => d[ft.plural.toLowerCase()]?.active ?? 0,
);
const ftColor = (ft) => {
  const cls = ft.iconClass.split(" ")[0].replace("text-", "");
  return /\d/.test(cls) ? `var(--color-${cls})` : `var(--color-${cls}-500)`;
};
const colors = findingTypes.map(ftColor);
const inactive = ref<boolean[]>(findingTypes.map(() => false));
const legendItems = computed(() =>
  findingTypes.map((ft, i) => ({
    name: ft.plural,
    color: ftColor(ft),
    inactive: inactive.value[i],
  })),
);
const onLegendItemClick = (_: unknown, i: number) => {
  inactive.value = inactive.value.map((v, j) => (j === i ? !v : v));
};
const activeY = computed(() =>
  y.map((accessor, i) => (inactive.value[i] ? null : accessor)),
);
const tickValues = computed(() =>
  data.value.map((d) => new Date(d.month).getTime()),
);
const formatMonth = (ts: number) =>
  new Date(ts).toLocaleDateString(undefined, {
    month: "short",
    year: "numeric",
  });

function processStats() {
  const byMonth = {};
  findingTypes.forEach((ft) => {
    const key = ft.plural.toLowerCase();
    (stats.value[key] ?? []).forEach((point) => {
      if (!byMonth[point.month]) byMonth[point.month] = { month: point.month };
      byMonth[point.month][key] = {
        active: point.active,
        discovered: point.discovered,
        fixed: point.fixed,
      };
    });
  });
  const now = new Date();
  const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
  if (!byMonth[currentMonth]) byMonth[currentMonth] = { month: currentMonth };
  findingTypes.forEach((ft) => {
    const key = ft.plural.toLowerCase();
    if (!byMonth[currentMonth][key]) {
      const series = stats.value[key] ?? [];
      if (series.length) {
        byMonth[currentMonth][key] = {
          active: series[series.length - 1].active,
          discovered: 0,
          fixed: 0,
        };
      }
    }
  });
  return Object.values(byMonth).sort((a, b) => a.month.localeCompare(b.month));
}

function tooltip(d) {
  const month = formatMonth(new Date(d.month).getTime());
  const cells = findingTypes
    .filter((ft, i) => d[ft.plural.toLowerCase()] && !inactive.value[i])
    .flatMap((ft) => {
      const vals = d[ft.plural.toLowerCase()];
      const extras: string[] = [];
      if (vals.discovered > 0)
        extras.push(
          `<span style="color:#ef4444">+${formatCount(vals.discovered)}</span>`,
        );
      if (vals.fixed > 0)
        extras.push(
          `<span style="color:#22c55e">−${formatCount(vals.fixed)}</span>`,
        );
      return [
        `<span style="width:10px;height:10px;border-radius:50%;background:${ftColor(ft)};display:inline-block"></span>`,
        `<span style="font-size:12px">${ft.plural}</span>`,
        `<span style="font-weight:600;text-align:right">${formatCount(vals.active)}</span>`,
        `<span style="font-size:11px;display:flex;gap:4px">${extras.join("")}</span>`,
      ];
    })
    .join("");
  return `<div style="padding:10px 14px;min-width:220px">
    <div style="font-weight:600;font-size:13px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid rgba(128,128,128,0.25)">${month}</div>
    <div style="display:grid;grid-template-columns:10px 1fr auto auto;gap:4px 8px;align-items:center">${cells}</div>
  </div>`;
}

function fetch() {
  loading.value = true;
  return Promise.all(
    findingTypes.map((ft) =>
      api
        .get(
          `${ft.value.toLowerCase()}-evolution/${props.project ? `?project=${props.project}` : ""}`,
        )
        .then((response) => (stats.value[ft.plural.toLowerCase()] = response)),
    ),
  ).finally(() => (loading.value = false));
}

onMounted(async () => {
  await fetch();
  await nextTick();
  if (container.value) {
    container.value.scrollLeft = container.value.scrollWidth;
  }
});
</script>
