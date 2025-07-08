<template>
  <v-dialog width="100%" fullscreen>
    <template #activator="{ props: activatorProps }">
      <BaseButton
        hover
        icon="mdi-notebook-plus"
        :icon-color="iconColor"
        :color="color"
        :size="size"
        :variant="variant"
        v-bind="activatorProps"
        tooltip="Take a note"
        @click.prevent.stop
      />
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
  execution: { type: Object, required: false, default: null },
  osint: { type: Object, required: false, default: null },
  host: { type: Object, required: false, default: null },
  port: { type: Object, required: false, default: null },
  path: { type: Object, required: false, default: null },
  credential: { type: Object, required: false, default: null },
  technology: { type: Object, required: false, default: null },
  vulnerability: { type: Object, required: false, default: null },
  exploit: { type: Object, required: false, default: null },
  variant: { type: String, required: false, default: "text" },
  iconColor: { type: String, required: false, default: "indigo-darken-1" },
  color: { type: String, required: false, default: undefined },
  size: { type: String, required: false, default: "x-large" },
});
defineEmits(["completed"]);
</script>
