<template>
  <div
    v-if="total > 0 || loading"
    class="grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-8 gap-3"
  >
    <template v-for="item in counters" :key="item.plural">
      <FindingsCounter
        :task-id="taskId"
        :project-id="projectId"
        :counter="item"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { findingTypes } from "~/constants";

const props = defineProps<{
  taskId?: string | number;
  projectId?: string | number;
}>();

const api = useApi("/api/");
const total = ref(0);
const loading = ref(false);
const counters = ref(
  findingTypes.map((ft) => ({
    ...ft,
    count: 0,
    loading: false,
  })),
);

function fetch() {
  total.value = 0;
  loading.value = true;
  counters.value.forEach((c) => {
    c.loading = true;
  });
  counters.value.forEach((counter, index) => {
    api
      .list(
        `${counter.plural.toLowerCase()}/`,
        props.taskId
          ? { task: props.taskId }
          : props.projectId
            ? { project: props.projectId }
            : {},
        false,
        1,
        1,
      )
      .then((response) => {
        counters.value[index].count = response.total;
        total.value += response.total;
      })
      .catch(() => {
        counters.value[index].count = 0;
      })
      .finally(() => {
        counters.value[index].loading = false;
        loading.value = counters.value.some((c) => c.loading);
      });
  });
}

onMounted(fetch);

defineExpose({ fetch });
</script>
