<template>
  <UButton
    icon="i-lucide-play"
    color="success"
    variant="solid"
    :class="['font-bold', notRounded ? undefined : 'rounded-full']"
    :label="label"
    aria-label="Run scan"
    :size="size"
    @click="openModal = !openModal"
  />
  <LazyCrudFormModal
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
import type {
  Process,
  Project,
  Configuration,
  Tool,
  Target,
  TargetPort,
} from "~/types/models";
import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";

const props = defineProps<{
  project?: Project;
  target?: Target;
  targetPort?: TargetPort;
  tool?: Tool;
  process?: Process;
  configuration?: Configuration;
  label?: string;
  notRounded?: boolean;
  size?: string;
}>();

const api = useApi("/api/tasks/");
const breakpoints = useBreakpoints(breakpointsTailwind);
const config = reactive({
  entityName: "Scan",
  editForm: resolveComponent("TasksForm"),
  onCreation: (data: Record<string, unknown>) => {
    return navigateTo(`/projects/${data.target.project}/scans/${data.id}`);
  },
  modalAvatar: () =>
    props.tool && props.tool.icon ? { src: props.tool.icon } : undefined,
  modalIcon: () =>
    props.tool && !props.tool.icon ? "i-lucide-square-terminal" : undefined,
  formFullscreen: breakpoints.smaller("lg"),
});
const openModal = ref(false);

function open() {
  openModal.value = true;
}

defineExpose({ open });
</script>
