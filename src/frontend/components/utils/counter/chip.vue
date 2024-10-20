<template>
  <v-chip
    class="mr-4"
    :prepend-icon="icon"
    :color="color"
    :link="link !== null"
    :target="newTab ? '_blank' : '_self'"
    @click.stop
  >
    {{ display }} {{ entity }}
  </v-chip>
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
