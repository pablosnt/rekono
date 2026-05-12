<template>
  <div class="space-y-4 mx-auto mt-3">
    <UFormField v-if="!defaultProject" required label="Project" name="project">
      <USelectMenu
        :model-value="project"
        class="w-full"
        icon="i-lucide-folder"
        placeholder="Select a project"
        :items="projectOptions"
        value-key="id"
        label-key="name"
        description-key="none"
        size="xl"
        @update:model-value="(value) => onProject(value)"
      >
        <template #trailing>
          <UIcon
            v-if="!project"
            class="group-data-[state=open]:rotate-180 transition-transform duration-200"
            name="i-lucide-chevron-down"
          />
          <UButton
            v-else
            icon="i-lucide-x"
            variant="ghost"
            color="neutral"
            size="sm"
            aria-label="Clear project"
            @click="onProject(undefined)"
          />
        </template>
      </USelectMenu>
    </UFormField>
    <UFormField v-if="!defaultTarget" required label="Target" name="target">
      <USelectMenu
        :model-value="target"
        class="w-full"
        icon="i-lucide-locate-fixed"
        placeholder="Select a target"
        :items="targetOptions"
        value-key="id"
        label-key="target"
        size="xl"
        :disabled="!project"
        @update:model-value="(value) => onTarget(value)"
      >
        <template #trailing>
          <UIcon
            v-if="!target"
            class="group-data-[state=open]:rotate-180 transition-transform duration-200"
            name="i-lucide-chevron-down"
          />
          <UButton
            v-else
            icon="i-lucide-x"
            variant="ghost"
            color="neutral"
            size="sm"
            aria-label="Clear target"
            @click="onTarget(undefined)"
          />
        </template>
      </USelectMenu>
    </UFormField>
    <UFormField
      v-if="targetPortOptions.length > 0"
      label="Target Port"
      name="targetPort"
    >
      <USelectMenu
        :model-value="targetPort"
        class="w-full"
        :icon="
          targetPort
            ? targetPortOptions.find((option) => option.id === targetPort)?.icon
            : 'i-lucide-ethernet-port'
        "
        placeholder="Select a target port"
        :items="targetPortOptions"
        value-key="id"
        label-key="label"
        size="xl"
        :disabled="!target"
        @update:model-value="(value) => onTargetPort(value)"
      >
        <template #trailing>
          <UIcon
            v-if="!targetPort"
            class="group-data-[state=open]:rotate-180 transition-transform duration-200"
            name="i-lucide-chevron-down"
          />
          <UButton
            v-else
            icon="i-lucide-x"
            variant="ghost"
            color="neutral"
            size="sm"
            aria-label="Clear target port"
            @click="onTargetPort(undefined)"
          />
        </template>
      </USelectMenu>
    </UFormField>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  api: typeof useApi;
  defaultProject: number | undefined;
  defaultTarget: number | undefined;
}>();
const emit = defineEmits<{
  "update-target": [newTarget: number | undefined];
  "update-project": [newProject: number | undefined];
  "update-target-port": [newTargetPort: number | undefined];
  "update-target-port-options": [hasOptions: boolean];
}>();

const project = ref(props.defaultProject);
const projectOptions = ref([]);
const target = ref(props.defaultTarget);
const targetOptions = ref([]);
const targetPort = ref();
const targetPortOptions = ref([]);

function loadProjects() {
  props.api.list("projects/", {}, true).then((response) => {
    projectOptions.value = response.items;
  });
}

function onProject(projectId: number | undefined) {
  project.value = projectId;
  emit("update-project", projectId);
  target.value = undefined;
  emit("update-target", undefined);
  targetPort.value = undefined;
  emit("update-target-port", undefined);
  emit("update-target-port-options", false);
  if (projectId) {
    props.api
      .list("targets/", { project: projectId }, true)
      .then((response) => {
        targetOptions.value = response.items;
      });
  }
}

function onTarget(targetId: number | undefined) {
  target.value = targetId;
  emit("update-target", targetId);
  targetPort.value = undefined;
  emit("update-target-port", undefined);
  targetPortOptions.value = [];
  emit("update-target-port-options", false);
  if (targetId) {
    props.api
      .list("target-ports/", { target: targetId }, true)
      .then((response) => {
        targetPortOptions.value = response.items.map((port) => ({
          id: port.id,
          label: port.path
            ? `${port.port} - ${port.path}`
            : port.port.toString(),
          icon: getPortIcon(port.port),
        }));
        emit("update-target-port-options", response.items.length > 0);
      });
  }
}

function onTargetPort(targetPortId: number | undefined) {
  emit("update-target-port", targetPortId);
  targetPort.value = targetPortId;
}

onMounted(() => {
  if (props.defaultTarget) {
    onTarget(props.defaultTarget);
  } else if (props.defaultProject) {
    onProject(props.defaultProject);
  } else {
    loadProjects();
  }
});
</script>
