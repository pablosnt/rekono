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
  onlyActive?: boolean;
  isTriageable?: boolean;
  findingNamePlural: string;
}>();

const api = useApi("/api/");
const total = ref(0);
const loading = ref(false);
const findingType = ref(
  findingTypes.find((ft) => ft.plural === props.findingNamePlural) ?? {},
);
const openFindings = { is_fixed: false };
const activeFindings = {
  triage_status__in: "True Positive,Untriaged",
  ...openFindings,
};
const defaultFilters = props.onlyActive
  ? props.isTriageable
    ? activeFindings
    : openFindings
  : {};

function fetch() {
  total.value = 0;
  loading.value = true;
  api
    .list(
      `${props.findingNamePlural.toLowerCase()}/`,
      props.taskId
        ? { task: props.taskId, ...defaultFilters }
        : props.projectId
          ? { project: props.projectId, ...defaultFilters }
          : defaultFilters,
      false,
      1,
      1,
    )
    .then((response) => (total.value = response.total))
    .finally(() => (loading.value = false));
}

onMounted(fetch);
</script>
