<template>
  <!-- CODE: Review all the places where this can be used, and maybe, adapt it if needed -->
  <!-- CODE: Replace link name by button -->
  <!-- CODE: Avoid definining properties without default that can be automatically inherited in all occurrences -->
  <v-btn
    v-if="link || !hide"
    :color="color"
    :target="!link ? undefined : newTab ? '_blank' : '_self'"
    :href="link"
    :variant="variant"
    :icon="icon || avatar"
    :hover="link !== undefined"
    @click.prevent.stop
  >
    <v-avatar v-if="avatar" :size="avatarSize" :image="avatar" />
    <v-icon v-if="icon && !avatar" :color="iconColor" :icon="icon" />
    <v-tooltip
      v-if="tooltip !== undefined"
      activator="parent"
      :text="tooltip"
    />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({
  link: { type: String, required: false, default: undefined },
  variant: { type: String, required: false, default: "text" },
  icon: { type: String, required: false, default: "mdi-open-in-new" },
  iconColor: { type: String, required: false, default: undefined },
  avatar: { type: String, required: false, default: undefined },
  avatarSize: { type: String, required: false, default: "small" },
  color: { type: String, required: false, default: "medium-emphasis" },
  tooltip: { type: String, required: false, default: undefined },
  newTab: { type: Boolean, required: false, default: false },
  hide: { type: Boolean, required: false, default: false },
});
</script>
