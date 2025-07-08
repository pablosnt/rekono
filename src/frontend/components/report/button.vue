<template>
  <v-dialog width="auto">
    <template #activator="{ props: activatorProps }">
      <BaseButton
        hover
        :icon-color="iconColor"
        :color="color"
        :size="size"
        :variant="variant"
        v-bind="activatorProps"
        icon="mdi-file-document-plus"
        tooltip="Create a report"
      />
    </template>
    <template #default="{ isActive }">
      <!-- TODO: Review how creation is handled after that -->
      <ReportDialog
        :project="project"
        :target="target"
        :task="task"
        @close-dialog="isActive.value = false"
        @completed="
          isActive.value = false;
          $emit('completed');
        "
      />
    </template>
  </v-dialog>
</template>

<script setup lang="ts">
defineProps({
  project: { type: Number, required: false, default: null },
  target: { type: Object, required: false, default: null },
  task: { type: Object, required: false, default: null },
  variant: { type: String, required: false, default: "text" },
  iconColor: { type: String, required: false, default: "blue-grey-darken-2" },
  color: { type: String, required: false, default: undefined },
  size: { type: String, required: false, default: "x-large" },
});
defineEmits(["completed"]);
</script>
