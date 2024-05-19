<template>
  <DialogDefault
    title="Execution"
    :loading="loading"
    width="1000"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <template #default>
      <FormTask
        :api="api"
        :project="project"
        :target="target"
        :process="process"
        :tool="tool"
        :configuration="configuration"
        @loading="(value) => (loading = value)"
        @completed="
          loading = false;
          $emit('completed');
          $emit('closeDialog');
        "
      />
    </template>
  </DialogDefault>
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
});
const emit = defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
const api = useApi("/api/tasks/", true, "Task");
</script>
