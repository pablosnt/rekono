<template>
  <v-card :title="title" :subtitle="subtitle" variant="text">
    <template #prepend>
      <v-icon v-if="icon" :icon="icon" :color="iconColor" />
    </template>
    <template #append>
      <slot name="extra-append" />
      <v-btn
        v-if="project === null && target === null"
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
const props = defineProps({
  api: Object,
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
});
const emit = defineEmits(["stats"]);
const loading = ref(true);

props.api
  .get(
    null,
    props.project || props.target
      ? `?${props.target ? `target=${props.target.id}` : `project=${props.project.id}`}`
      : null,
  )
  .then((response) => {
    emit("stats", response);
    loading.value = false;
  });
</script>
