<template>
  <UButton
    v-if="show !== false"
    :icon="icon || 'i-lucide-plus'"
    :color="color"
    :variant="variant"
    @click="createNote"
  />
</template>

<script setup lang="ts">
const props = defineProps<{
  show?: boolean;
  project?: number;
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
  icon?: string;
  color?: string;
  variant?: string;
}>();
const api = useApi("/api/notes/");
const route = useRoute();

function createNote() {
  api
    .create("", {
      project: props.project || route.params.project_id,
      target_id: props.target,
      task_id: props.task,
      osint_id: props.osint,
      host_id: props.host,
      port_id: props.port,
      path_id: props.path,
      credential_id: props.credential,
      technology_id: props.technology,
      vulnerability_id: props.vulnerability,
      exploit_id: props.exploit,
      title: "Title",
      body: "",
      tags: [],
      public: false,
    })
    .then((response) =>
      navigateTo(`/projects/${response.project}/notes/${response.id}`),
    );
}

defineExpose({ createNote });
</script>
