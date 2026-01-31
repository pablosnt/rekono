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
    :ui="{
      content: 'sm:max-w-6xl sm:max-h-xl',
      footer: 'justify-end',
    }"
    @open="(open: boolean) => (openModal = open)"
  />
</template>

<script setup lang="ts">
import type { Process } from "~/types/processes";
import type { Project } from "~/types/projects";
import type { Configuration, Tool } from "~/types/tools";
import type { Target } from "~/types/target";
import type { TargetPort } from "~/types/target_ports";

const props = defineProps<{
  project?: Project;
  target?: Target;
  targetPort?: TargetPort;
  tool?: Tool;
  process?: Process;
  configuration?: Configuration;
}>();

const api = useApi("/api/tasks/");
const config = {
  entityName: "Scan",
  editForm: resolveComponent("TasksForm"),
  // todo: Redirection path is likely to be projects/project-id/scans/scan-id
  onCreation: (data: Record<string, unknown>) => navigateTo(`scans/${data.id}`),
  modalAvatar: () =>
    props.tool && props.tool.icon ? { src: props.tool.icon } : undefined,
  modalIcon: () =>
    props.tool && !props.tool.icon ? "i-lucide-square-terminal" : undefined,
};
const openModal = ref(false);
</script>
