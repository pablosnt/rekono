<template>
  <UButton
    icon="i-lucide-play"
    color="success"
    variant="solid"
    class="font-bold rounded-full"
    @click="openModal = !openModal"
  />
  <CrudFormModal
    :open="openModal"
    :api="api"
    :config="config"
    :item="{
      project: project?.id,
      target: target?.id,
      targetPort: targetPort?.id,
      tool: tool?.id,
      process: process?.id,
      configuration: configuration?.id,
    }"
    :title="
      configuration
        ? configuration.name
        : tool
          ? tool.name
          : process
            ? process.name
            : 'Customize Scan'
    "
    submit-label="Run"
    @open="(open: boolean) => (openModal = open)"
  />
</template>

<script setup lang="ts">
defineProps<{
  project?: number;
  target?: number;
  targetPort?: number;
  tool?: number;
  process?: number;
  configuration?: number;
}>();

const api = useApi("/api/tasks/");
const config = {
  entityName: "Scan",
  editForm: resolveComponent("TasksForm"),
  // todo: Redirection path is likely to be projects/project-id/scans/scan-id
  onCreation: (data: Record<string, unknown>) => navigateTo(`scans/${data.id}`),
};
const openModal = ref(false);
</script>
