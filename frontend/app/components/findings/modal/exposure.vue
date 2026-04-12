<template>
  <UModal
    title="Exposure Window"
    description="Dates when the finding has been detected"
    :open="open"
    :ui="{ content: 'sm:max-w-3xl sm:max-h-xl' }"
    @update:open="(value) => $emit('open', value)"
  >
    <template #body>
      <VisXYContainer :data="timeline" :x-domain="xDomain" :height="100">
        <VisTimeline :x="(d) => d.timestamp" :color="(d) => d.color" />
        <VisAxis
          type="x"
          :tick-format="(d: number) => new Date(d).toDateString()"
        />
        <VisTooltip :triggers="tooltipTriggers" />
      </VisXYContainer>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { VisXYContainer, VisTimeline, VisAxis, VisTooltip } from "@unovis/vue";
import { Timeline } from "@unovis/ts";
import type { Finding } from "~/types/models";

const props = defineProps<{
  open: boolean;
  finding?: Finding;
  dates?: Date[];
}>();
defineEmits<{ open: [open: boolean] }>();

const dailyMs = 60 * 60 * 24 * 1000;

const timeline = computed(() => {
  const data = (
    props.dates ? props.dates : getExposureWindow(props.finding)
  ).map((d) => ({
    timestamp: d.date.getTime(),
    length: dailyMs,
    color: "var(--color-primary-500)",
    type: "Timeline",
    fixed: false,
    tools: d.tools,
  }));
  if (props.finding?.fixed_date) {
    data.push({
      timestamp: new Date(props.finding.fixed_date).getTime(),
      length: dailyMs,
      color: "var(--color-success-500)",
      type: "Timeline",
      fixed: true,
      tools: [],
    });
  }
  return data;
});

const tooltipTriggers = {
  [Timeline.selectors.line]: (d) => {
    const date = new Date(d.timestamp).toDateString();
    return d.fixed
      ? props.finding?.auto_fixed
        ? `Automatically fixed on ${date}`
        : `Fixed${props.finding.fixed_by ? ` by ${props.finding.fixed_by.username}` : ""} on ${date}`
      : `Detected${d.tools.length > 0 ? ` by ${d.tools.join(", ")}` : ""} on ${date}`;
  },
};

const xDomain = computed<[number, number] | undefined>(() => {
  if (timeline.value.length < 2) return undefined;
  return [
    timeline.value[0]?.timestamp - dailyMs,
    timeline.value[timeline.value.length - 1]?.timestamp + dailyMs * 2,
  ];
});
</script>
