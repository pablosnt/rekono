<template>
  <!-- TODO: Hardcode in task_id page -->
  <v-card
    :title="execution.configuration.name"
    :subtitle="execution.configuration.tool.name"
    variant="outlined"
    :hover="['Completed', 'Error'].includes(execution.status)"
  >
    <template #prepend>
      <!-- todo: why not using prepend-avatar as Dialog does? Do the same everywhere -->
      <v-avatar
        v-if="execution.configuration.tool.icon"
        :image="execution.configuration.tool.icon"
      />
      <v-icon
        v-if="!execution.configuration.tool.icon"
        icon="mdi-rocket"
        color="red"
      />
    </template>
    <template #text>
      <p v-if="execution.start">
        <span class="text-medium-emphasis">Time:</span>
        {{ new Date(execution.start).toUTCString() }}
      </p>
      <p v-if="execution.start && execution.end">
        <span class="text-medium-emphasis">Duration:</span>
        {{ dates.getDuration(execution.start, execution.end) }}
      </p>

      <p
        v-if="execution.status === 'Skipped' && execution.skipped_reason"
        class="text-center font-weight-light"
      >
        {{ execution.skipped_reason }}
      </p>
    </template>
    <v-card-actions>
      <ExecutionReportButton :api="api" :execution="execution" />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
defineProps({ api: Object, execution: Object });
const dates = useDates();
</script>
