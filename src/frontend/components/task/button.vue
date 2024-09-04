<template>
  <v-dialog width="auto">
    <template #activator="{ props: activatorProps }">
      <v-btn
        hover
        icon
        size="x-large"
        v-bind="activatorProps"
        variant="text"
        @click.prevent.stop
      >
        <v-icon icon="mdi-play-circle" color="green" />
        <v-tooltip activator="parent" :text="tooltip" />
      </v-btn>
    </template>
    <template #default="{ isActive }">
      <TaskDialog
        :project="project"
        :target="target"
        :process="process"
        :tool="tool"
        :configuration="configuration"
        @close-dialog="isActive.value = false"
      />
    </template>
  </v-dialog>
</template>

<script setup lang="ts">
defineProps({
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
  process: {
    type: Object,
    required: false,
    default: null,
  },
  tool: {
    type: Object,
    required: false,
    default: null,
  },
  configuration: {
    type: Object,
    required: false,
    default: null,
  },
  tooltip: {
    type: String,
    required: false,
    default: "Scan",
  },
});
</script>
