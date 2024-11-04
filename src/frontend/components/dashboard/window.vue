<template>
  <v-card :title="title" :subtitle="subtitle" variant="text">
    <template #prepend>
      <v-icon v-if="icon" :icon="icon" :color="iconColor" />
    </template>
    <template #append>
      <slot name="extra-append" />
      <v-btn
        v-if="target !== null || (project === null && target === null)"
        variant="text"
        icon
        color="medium-emphasis"
        to="/projects"
        hover
      >
        <v-icon icon="mdi-folder-open" />
        <v-tooltip activator="parent" text="All projects" />
      </v-btn>
      <TaskButton
        v-if="target !== null || (project === null && target === null)"
        :project="project"
        :target="target"
      />
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
  subtitle: {
    type: String,
    required: false,
    default: undefined,
  },
  icon: {
    type: String,
    required: false,
    default: undefined,
  },
  iconColor: {
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
  loading: {
    type: Boolean,
    required: false,
    default: null,
  },
});
// TODO: Move all API calls to here, as we did with dataset component
</script>
