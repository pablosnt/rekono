<template>
  <!-- TODO: Test and remove -->
  <!-- <v-btn
    :variant="variant"
    :target="link ? '_blank' : undefined"
    :href="
      !link
        ? undefined
        : project.defect_dojo_sync.engagement_id !== null
          ? `${settings.server}/engagement/${project.defect_dojo_sync.engagement_id}`
          : `${settings.server}/product/${project.defect_dojo_sync.product_id}`
    "
    icon
    :color="color ? 'blue-accent-3' : undefined"
    @click.stop
  >
    
    <v-avatar v-if="!icon" size="small" :image="integration.icon" />
    <v-icon v-if="icon" :icon="icon" />
  </v-btn> -->
  <!-- TODO: review color after and update icon -->
  <BaseLink
    :link="
      !link
        ? undefined
        : project.defect_dojo_sync.engagement_id !== null
          ? `${settings.server}/engagement/${project.defect_dojo_sync.engagement_id}`
          : `${settings.server}/product/${project.defect_dojo_sync.product_id}`
    "
    :color="color ? 'blue-accent-3' : undefined"
    :avatar="!icon ? integration.icon : undefined"
    :icon="icon ? icon : undefined"
    :variant="variant"
    show-always
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
