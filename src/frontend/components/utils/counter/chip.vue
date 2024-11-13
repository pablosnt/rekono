<template>
  <v-chip
    class="mr-4"
    :prepend-icon="icon"
    :color="color"
    :link="link !== null"
    :target="newTab ? '_blank' : '_self'"
    :variant="variant"
    :disabled="disabled"
    @click.stop="$emit('click')"
  >
    {{ display }} {{ entity }}
  </v-chip>
  <!-- CODE: Test if it's needed to retrigger the click event -->
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
  disabled: {
    type: Boolean,
    required: false,
    default: false,
  },
});
defineEmits(["click"]);
</script>
