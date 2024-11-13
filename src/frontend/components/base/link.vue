<template>
  <!-- CODE: Review all the places where this can be used, and maybe, adapt it if needed -->
  <v-btn
    v-if="link || showAlways"
    :variant="variant"
    :color="color"
    :target="sameTab ? '_self' : '_blank'"
    :href="link"
    :size="size"
    icon
    :hover="link !== undefined"
  >
    <v-avatar v-if="avatar" :size="avatarSize" :image="avatar" />
    <v-icon v-if="!avatar" :icon="icon" />
    <v-tooltip
      v-if="tooltip !== undefined"
      activator="parent"
      :text="tooltip"
    />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({
  link: String,
  variant: { type: String, required: false, default: "text" },
  icon: { type: String, required: false, default: "mdi-open-in-new" },
  avatar: { type: String, required: false, default: undefined },
  avatarSize: { type: String, required: false, default: "small" },
  size: { type: String, required: false, default: undefined },
  color: { type: String, required: false, default: "medium-emphasis" },
  tooltip: { type: String, required: false, default: undefined },
  sameTab: { type: Boolean, required: false, default: false },
  showAlways: { type: Boolean, required: false, default: false },
});
</script>
