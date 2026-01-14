<template>
  <div class="space-y-4 mx-auto mt-3">
    <UFormField v-if="!defaultProject" required label="Project">
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
            @click="onProject(undefined)"
          />
        </template>
      </USelectMenu>
    </UFormField>
    <UFormField v-if="!defaultTarget" required label="Target">
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
            @click="onTarget(undefined)"
          />
        </template>
      </USelectMenu>
    </UFormField>
    <UFormField label="Target Port">
      <!-- TODO: Customize target port icon based on the port number as we did on the old frontend -->
      <USelectMenu
        :model-value="targetPort"
        class="w-full"
        icon="i-lucide-network"
        placeholder="Select a target port"
        :items="
          targetPortOptions.map((port) => ({
            id: port.id,
            label: port.path
              ? `${port.port} - ${port.path}`
              : port.port.toString(),
          }))
        "
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
            @click="onTargetPort(undefined)"
          />
        </template>
      </USelectMenu>
    </UFormField>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  api: object;
  defaultProject: number | undefined;
  defaultTarget: number | undefined;
}>();
const emit = defineEmits<{
  "update-target": [newTarget: number | undefined];
  "update-project": [newProject: number | undefined];
  "update-target-port": [newTargetPort: number | undefined];
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
  if (targetId) {
    props.api
      .list("target-ports/", { target: targetId }, true)
      .then((response) => {
        targetPortOptions.value = response.items;
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
