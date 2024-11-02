<template>
  <v-card :title="title" variant="text" :prepend-icon="icon">
    <template #append>
      <slot name="extra-append" />
      <TaskButton :project="project" :target="target" />
    </template>
    <template #text>
      <slot />
    </template>
  </v-card>
</template>

<script setup lang="ts">
defineProps({
  title: String,
  icon: {
    type: String,
    required: false,
    default: undefined,
  },
  project: {
    type: Object,
    required: false,
    default: null,
  },
  target: {
    type: Object,
    required: false,
    default: null,
  },
});
</script>
