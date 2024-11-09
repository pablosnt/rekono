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
        <v-icon icon="mdi-file-document-plus" color="blue-grey-darken-2" />
        <v-tooltip activator="parent" text="Create a report" />
      </v-btn>
    </template>
    <template #default="{ isActive }">
      <!-- TODO: Review how creation is handled after that -->
      <ReportDialog
        :project="project"
        :target="target"
        :task="task"
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
});
</script>
