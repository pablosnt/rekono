<template>
  <!-- TODO: review color after and update icon -->
  <BaseButton
    v-if="integration.enabled && settings.is_available"
    :link="
      target.defectdojo_sync && target.defectdojo_sync.engagement_id
        ? `${settings.server}/engagement/${target.defectdojo_sync.engagement_id}`
        : undefined
    "
    color="blue-accent-3"
    :avatar="integration && integration.icon ? integration.icon : undefined"
    :variant="variant"
    new-tab
    hide
  />
</template>

<script setup lang="ts">
defineProps({
  target: Object,
  settings: Object,
  integration: Object,
  variant: { type: String, required: false, default: "tonal" },
});
</script>
