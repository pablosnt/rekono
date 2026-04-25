<template>
  <FindingsCounter
    :task-id="taskId"
    :project-id="projectId"
    :counter="{ ...findingType, count: total, loading: loading }"
  />
</template>

<script setup lang="ts">
import { findingTypes } from "~/constants";

const props = defineProps<{
  taskId?: string | number;
  projectId?: string | number;
  findingNamePlural: string;
}>();

const api = useApi("/api/");
const total = ref(0);
const loading = ref(false);
const findingType = ref(
  findingTypes.find((ft) => ft.plural === props.findingNamePlural) ?? {},
);

function fetch() {
  total.value = 0;
  loading.value = true;
  api
    .list(
      props.findingNamePlural.toLowerCase(),
      props.taskId
        ? { task: props.taskId }
        : props.projectId
          ? { project: props.projectId }
          : {},
      false,
      1,
      1,
    )
    .then((response) => (total.value = response.total))
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>
