<template>
  <v-btn
    class="mr-4 text-none"
    :icon="icon !== undefined || image !== undefined"
    variant="text"
    :to="link"
    :hover="link !== null"
    :target="newTab ? '_blank' : '_self'"
    stacked
  >
    <v-badge :content="display">
      <v-avatar
        v-if="size === undefined"
        :icon="icon"
        :image="image"
        :color="color"
        :variant="variant"
      />
      <v-icon
        v-if="size !== undefined"
        :icon="icon"
        :size="size"
        :color="color"
        :variant="variant"
      />
    </v-badge>
    <v-tooltip v-if="tooltip !== null" activator="parent" :text="tooltip" />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({
  value: Number,
  display: String,
  icon: {
    type: String,
    required: false,
    default: undefined,
  },
  image: {
    type: String,
    required: false,
    default: undefined,
  },
  size: {
    type: String,
    required: false,
    default: undefined,
  },
  variant: {
    type: String,
    required: false,
    default: "tonal",
  },
  color: {
    type: String,
    required: false,
    default: "red",
  },
  link: {
    type: String,
    required: false,
    default: null,
  },
  newTab: {
    type: Boolean,
    required: false,
    default: false,
  },
  tooltip: {
    type: String,
    required: false,
    default: null,
  },
  entity: {
    type: String,
    required: false,
    default: null,
  },
});
</script>
