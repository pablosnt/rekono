<template>
  <!-- TODO: review color after and update icon -->
  <BaseButton
    :link="
      !link
        ? undefined
        : project.defectdojo_sync.engagement_id !== null
          ? `${settings.server}/engagement/${project.defectdojo_sync.engagement_id}`
          : `${settings.server}/product/${project.defectdojo_sync.product_id}`
    "
    :color="color ? 'blue-accent-3' : undefined"
    :avatar="!icon ? integration.icon : undefined"
    :icon="icon ? icon : undefined"
    :variant="variant"
    new-tab
  />
</template>

<script setup lang="ts">
defineProps({
  project: Object,
  settings: Object,
  integration: Object,
  variant: { type: String, required: false, default: "text" },
  icon: { type: String, required: false, default: undefined },
  color: { type: Boolean, required: false, default: false },
  link: { type: Boolean, required: false, default: false },
});
</script>
