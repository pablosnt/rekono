<template>
  <v-dialog width="100%" fullscreen>
    <template #activator="{ props: activatorProps }">
      <v-btn
        hover
        icon
        size="x-large"
        v-bind="activatorProps"
        variant="text"
        @click.prevent.stop
      >
        <v-icon icon="mdi-note-plus" color="indigo-darken-1" />
        <v-tooltip activator="parent" text="Take a note" />
      </v-btn>
    </template>
    <template #default="{ isActive }">
      <NoteDialog
        :project="project"
        :target="target"
        :task="task"
        :execution="execution"
        :osint="osint"
        :host="host"
        :port="port"
        :path="path"
        :credential="credential"
        :technology="technology"
        :vulnerability="vulnerability"
        :exploit="exploit"
        @close-dialog="isActive.value = false"
      />
    </template>
  </v-dialog>
</template>

<script setup lang="ts">
defineProps({
  project: {
    type: Number,
    required: false,
    default: null,
  },
  target: {
    type: Object,
    required: false,
    default: null,
  },
  task: {
    type: Object,
    required: false,
    default: null,
  },
  execution: {
    type: Object,
    required: false,
    default: null,
  },
  osint: {
    type: Object,
    required: false,
    default: null,
  },
  host: {
    type: Object,
    required: false,
    default: null,
  },
  port: {
    type: Object,
    required: false,
    default: null,
  },
  path: {
    type: Object,
    required: false,
    default: null,
  },
  credential: {
    type: Object,
    required: false,
    default: null,
  },
  technology: {
    type: Object,
    required: false,
    default: null,
  },
  vulnerability: {
    type: Object,
    required: false,
    default: null,
  },
  exploit: {
    type: Object,
    required: false,
    default: null,
  },
});
</script>
