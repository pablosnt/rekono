<template>
  <div v-if="tools" class="d-flex flex-row justify-center ga-2">
    <utils-counter
      v-for="tool in tools"
      :key="tool"
      :number="counters[tool].count"
      :image="counters[tool].icon ? counters[tool].icon : undefined"
      :icon="!counters[tool].icon ? 'mdi-rocket' : undefined"
      :color="!counters[tool].icon ? 'red' : undefined"
      :variant="!counters[tool].icon ? 'tonal' : undefined"
      :tooltip="`${tool} detections`"
      :link="
        counters[tool].lastTask
          ? `/projects/${route.params.project_id}/scans/${counters[tool].lastTask}`
          : undefined
      "
      new-tab
    />
  </div>
</template>

<script setup lang="ts">
const props = defineProps({ finding: Object });
const emit = defineEmits(["exposure"]);
const route = useRoute();
const dates = useDates();
const api = useApi("/api/executions/", true);
const counters = ref({});
let first = null;

for (const execution of props.finding.executions) {
  if (first === null || execution.id < first) {
    first = execution.id;
  }
  if (counters.value[execution.configuration.tool.name]) {
    counters.value[execution.configuration.tool.name].count++;
    if (
      counters.value[execution.configuration.tool.name].lastTask <
      execution.task
    ) {
      counters.value[execution.configuration.tool.name].lastTask =
        execution.task;
    }
  } else {
    counters.value[execution.configuration.tool.name] = {
      count: 1,
      icon: execution.configuration.tool.icon,
      reference: execution.configuration.tool.reference,
      lastTask: execution.task,
    };
  }
}

if (first !== null) {
  api.get(first).then((firstExecution) => {
    emit(
      "exposure",
      dates.getDuration(
        firstExecution.start,
        props.finding.is_fixed ? props.finding.fixed_date : null,
        true,
      ),
    );
  });
}

const tools = ref(Object.keys(counters.value));
</script>
