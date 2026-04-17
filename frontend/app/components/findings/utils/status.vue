<template>
  <UTooltip
    v-if="finding.is_fixed"
    :text="
      finding.auto_fixed
        ? `Auto-${fixVerb}ed`
        : `${fixVerb}ed by ${finding.fixed_by.username} ${useTimeAgo(new Date(finding.fixed_date))}`
    "
    :content="{ side: 'left', sideOffset: 8, collisionPadding: 8 }"
  >
    <UButton
      :icon="
        finding.auto_fixed
          ? 'i-lucide-bot'
          : fixVerb === 'Fix'
            ? 'i-lucide-badge-check'
            : 'i-lucide-eye-off'
      "
      :color="fixVerb === 'Fix' ? 'success' : 'neutral'"
      variant="subtle"
      :label="`${fixVerb}ed`"
      size="sm"
    />
  </UTooltip>
  <UTooltip
    v-else-if="isTriageable"
    :text="
      finding.triage_by && finding.triage_date
        ? `Triaged by ${finding.triage_by.username} ${useTimeAgo(new Date(finding.triage_date)).value}`
        : undefined
    "
    :content="{ side: 'left', sideOffset: 8, collisionPadding: 8 }"
  >
    <UButton
      :icon="triageConfig?.icon"
      :color="triageConfig?.color"
      variant="subtle"
      :label="triageConfig?.value"
      size="sm"
    />
  </UTooltip>
  <UBadge
    v-else
    icon="i-lucide-shield-alert"
    variant="subtle"
    :color="fixVerb === 'Fix' ? 'neutral' : 'success'"
    >Active</UBadge
  >
</template>

<script setup lang="ts">
import type { Finding } from "~/types/models";
import { useTimeAgo } from "@vueuse/core";
import { triageStatuses } from "~/constants";

const props = defineProps<{
  finding: Finding;
  isTriageable?: boolean;
  fixVerb: string;
}>();
const triageConfig = computed(() =>
  props.isTriageable
    ? triageStatuses.find((s) => s.value === props.finding.triage_status)
    : undefined,
);
</script>
