<template>
  <v-card :title="title" variant="text">
    <template #prepend>
      <v-icon v-if="icon" :icon="icon" :color="iconColor"/>
    </template>
    <template #append>
      <slot name="extra-append" />
      <v-btn variant="text" icon color="medium-emphasis" to="/projects" hover>
        <v-icon icon="mdi-folder-open" />
        <v-tooltip activator="parent" text="All projects" />
      </v-btn>
      <TaskButton :project="project" :target="target" />
    </template>
    <template #text>
      <v-container v-if="loading" fluid>
        <v-row justify="center" dense>
          <v-progress-circular
      color="red-lighten-1"
      indeterminate
      :size="100"
      :width="10"
    /></v-row>
        </v-container>
      <slot v-if="!loading" />
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
  iconColor: {
    type: String,
    required: false,
    default: undefined
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
  loading: {
    type: Boolean,
    required: false,
    default: null
  }
});
</script>
