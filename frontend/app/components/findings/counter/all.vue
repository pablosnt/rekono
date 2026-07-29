<template>
  <div
    v-if="showEmpty || loading || total > 0"
    class="grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-8 gap-3"
  >
    <div v-if="loading" class="sr-only" role="status">Loading findings summary</div>
    <template v-for="item in counters" :key="item.plural">
      <FindingsCounter
        :task-id="taskId"
        :target-id="targetId"
        :project-id="projectId"
        :counter="item"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { findingTypes } from "~/constants";

const props = defineProps<{
  taskId?: number;
  targetId?: number;
  projectId?: number;
  onlyActive?: boolean;
  showEmpty?: boolean;
}>();

const api = useApi("/api/");
const loading = ref(false);
const counters = ref(
  findingTypes.map((ft) => Object.assign({ count: 0, loading: true }, ft)),
);
const total = computed(() =>
  counters.value.reduce((sum, c) => sum + (c.count as number), 0),
);

function getFilters(isTriageable: boolean) {
  const defaultFilters = props.onlyActive
    ? isTriageable
      ? { triage_status__in: "True Positive,Untriaged", is_fixed: false }
      : { is_fixed: false }
    : {};
  return props.taskId
    ? { task: props.taskId, ...defaultFilters }
    : props.targetId
      ? { target: props.targetId, ...defaultFilters }
      : props.projectId
        ? { project: props.projectId, ...defaultFilters }
        : defaultFilters;
}

function fetch() {
  loading.value = true;
  counters.value.forEach((c) => {
    c.loading = true;
  });
  counters.value.forEach((counter, index) => {
    api
      .list(
        `${counter.plural.toLowerCase()}/`,
        getFilters(counter.isTriageable),
        false,
        1,
        1,
      )
      .then((response) => (counters.value[index].count = response.total))
      .catch(() => (counters.value[index].count = 0))
      .finally(() => {
        counters.value[index].loading = false;
        loading.value = counters.value.some((c) => c.loading);
      });
  });
}

onMounted(fetch);

defineExpose({ fetch });
</script>
