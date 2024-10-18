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
      new-tab
    />
    <!-- TODO: Link to latest task where the issue was found by each tool -->
  </div>
</template>

<script setup lang="ts">
const props = defineProps({ finding: Object });
const tools = ref([]);
const counters = ref({});

for (let i = 0; i < props.finding.executions.length; i++) {
  if (counters.value[props.finding.executions[i].configuration.tool.name]) {
    counters.value[props.finding.executions[i].configuration.tool.name].count++;
  } else {
    counters.value[props.finding.executions[i].configuration.tool.name] = {
      count: 1,
      icon: props.finding.executions[i].configuration.tool.icon,
      reference: props.finding.executions[i].configuration.tool.reference,
    };
  }
}

tools.value = Object.keys(counters.value);
</script>
