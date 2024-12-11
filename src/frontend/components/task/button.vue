<template>
  <v-dialog v-if="autz.isAuditor()" width="auto">
    <template #activator="{ props: activatorProps }">
      <BaseButton
        hover
        icon="mdi-play-circle"
        icon-color="green"
        :tooltip="tooltip"
        :disabled="disabled"
        size="x-large"
        v-bind="activatorProps"
        @click.prevent.stop
      />
    </template>
    <template #default="{ isActive }">
      <TaskDialog
        :project="project"
        :target="target"
        :process="process"
        :tool="tool"
        :configuration="configuration"
        @close-dialog="isActive.value = false"
        @reload="
          isActive.value = false;
          $emit('reload');
        "
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
  disabled: {
    type: Boolean,
    required: false,
    default: false,
  },
});
defineEmits(["reload"]);
const autz = useAutz();
</script>
