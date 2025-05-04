<template>
  <v-avatar
    v-if="task.configuration && task.configuration.tool.icon"
    :image="task.configuration.tool.icon"
  />
  <v-icon v-if="task.process" icon="mdi-robot-angry" color="red" />
  <v-icon
    v-if="task.configuration && !task.configuration.tool.icon"
    icon="mdi-rocket"
    color="red"
  />
</template>

<script setup lang="ts">
defineProps({ task: Object });
</script>
