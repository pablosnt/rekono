<template>
  <v-chip
    color="red"
    :to="`/projects/${route.params.project_id}/targets/${task.target.id}`"
    target="_blank"
    @click.stop
  >
    <v-icon icon="mdi-target" start />
    {{ task.target.target }}
  </v-chip>
</template>

<script setup lang="ts">
defineProps({ task: Object });
const route = useRoute();
</script>
