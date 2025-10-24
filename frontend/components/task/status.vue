<template>
  <v-progress-circular
    v-if="task.status && task.status === 'Running'"
    :model-value="task.progress"
    size="50"
    width="5"
    class="mr-3"
    color="amber"
  >
    <template #default>{{ task.progress }}%</template>
  </v-progress-circular>
  <v-chip
    v-if="task.status && task.status !== 'Running'"
    class="mr-3"
    :color="enums.statuses[task.status].color"
  >
    <v-icon :icon="enums.statuses[task.status].icon" start />
    {{ task.status }}
  </v-chip>
</template>

<script setup lang="ts">
defineProps({ task: Object });
const enums = useEnums();
</script>
