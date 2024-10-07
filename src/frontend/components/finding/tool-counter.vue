<template>
  <div v-if="tools" class="d-flex flex-row justify-center ga-2">
    <v-btn
      v-for="tool in tools"
      :key="tool"
      icon
      hover
      color="medium-emphasis"
      variant="text"
      :href="counters[tool].reference"
      target="_blank"
    >
      <v-badge
        floating
        :content="
          counters[tool].count < 1000
            ? counters[tool].count
            : Math.floor(counters[tool].count / 1000).toString() + 'k'
        "
      >
        <v-avatar v-if="counters[tool].icon" :image="counters[tool].icon" />
        <v-avatar
          v-if="!counters[tool].icon"
          icon="mdi-rocket"
          color="red"
          variant="tonal"
        />
      </v-badge>
      <v-tooltip activator="parent" :text="`${tool} detections`" />
    </v-btn>
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
