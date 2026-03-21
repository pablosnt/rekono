<template>
  <UButton v-if="show !== false" icon="i-lucide-plus" @click="createNote" />
</template>

<script setup lang="ts">
const props = defineProps<{
  show?: boolean;
  target?: number;
  task?: number;
  osint?: number;
  host?: number;
  port?: number;
  path?: number;
  credential?: number;
  technology?: number;
  vulnerability?: number;
  exploit?: number;
}>();
const api = useApi("/api/notes/");
const route = useRoute();

function createNote() {
  api
    .create("", {
      project: route.params.project_id,
      target: props.target,
      task: props.task,
      osint: props.osint,
      host: props.host,
      port: props.port,
      path: props.path,
      credential: props.credential,
      technology: props.technology,
      vulnerability: props.vulnerability,
      exploit: props.exploit,
      title: "Title",
      body: "# Subtitle",
      tags: [],
      public: false,
    })
    .then((response) =>
      navigateTo(`/projects/${route.params.project_id}/notes/${response.id}`),
    );
}

defineExpose({ createNote });
</script>
