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
const route = useRoute();
const tools = ref([]);
const counters = ref({});

for (let i = 0; i < props.finding.executions.length; i++) {
  if (counters.value[props.finding.executions[i].configuration.tool.name]) {
    counters.value[props.finding.executions[i].configuration.tool.name].count++;
    if (
      counters.value[props.finding.executions[i].configuration.tool.name].id <
      props.finding.executions[i].id
    ) {
      counters.value[props.finding.executions[i].configuration.tool.name].id =
        props.finding.executions[i].id;
    }
  } else {
    counters.value[props.finding.executions[i].configuration.tool.name] = {
      count: 1,
      icon: props.finding.executions[i].configuration.tool.icon,
      reference: props.finding.executions[i].configuration.tool.reference,
      lastExecution: props.finding.executions[i].id,
      lastTask: null,
    };
  }
}

tools.value = Object.keys(counters.value);
for (let i = 0; i < tools.value.length; i++) {
  useApi("/api/executions/", true)
    .get(counters.value[tools.value[i]].lastExecution)
    .then(
      (response) => (counters.value[tools.value[i]].lastTask = response.task),
    );
}
</script>
