<template>
  <v-btn
    v-if="route || link || !hide"
    :color="color"
    :target="!link ? undefined : newTab ? '_blank' : '_self'"
    :to="route"
    :href="link"
    :variant="variant"
    :icon="icon !== undefined || avatar !== undefined"
    :hover="link !== undefined || route !== undefined"
    @click.stop
  >
    <slot>
      <slot name="prepend" />
      <slot name="icon">
        <v-avatar v-if="avatar" :size="avatarSize" :image="avatar" />
        <v-icon
          v-if="icon && !avatar"
          :size="iconSize"
          :color="iconColor"
          :icon="icon"
        />
      </slot>
      <v-tooltip
        v-if="tooltip !== undefined"
        activator="parent"
        :text="tooltip"
      />
    </slot>
  </v-btn>
</template>

<script setup lang="ts">
defineProps({
  route: { type: String, required: false, default: undefined },
  link: { type: String, required: false, default: undefined },
  variant: { type: String, required: false, default: "text" },
  icon: { type: String, required: false, default: "mdi-open-in-new" },
  iconColor: { type: String, required: false, default: undefined },
  iconSize: { type: String, required: false, default: undefined },
  avatar: { type: String, required: false, default: undefined },
  avatarSize: { type: String, required: false, default: "small" },
  color: { type: String, required: false, default: "medium-emphasis" },
  tooltip: { type: String, required: false, default: undefined },
  newTab: { type: Boolean, required: false, default: false },
  hide: { type: Boolean, required: false, default: false },
});
</script>
