<template>
  <v-chip v-if="entity" color="red" :to="link" target="_blank" @click.stop>
    <v-icon :icon="icon" start />
    {{ value }}
  </v-chip>
</template>

<script setup lang="ts">
const props = defineProps({
  target: { type: Object, required: false, default: null },
  task: { type: Object, required: false, default: null },
  execution: { type: Object, required: false, default: null },
  osint: { type: Object, required: false, default: null },
  host: { type: Object, required: false, default: null },
  port: { type: Object, required: false, default: null },
  path: { type: Object, required: false, default: null },
  credential: { type: Object, required: false, default: null },
  technology: { type: Object, required: false, default: null },
  vulnerability: { type: Object, required: false, default: null },
  exploit: { type: Object, required: false, default: null },
  note: { type: Object, required: false, default: null },
});
const route = useRoute();
const enums = useEnums();
const icon = ref(null);
const entity = ref(null);
const value = ref(null);
const link = ref(null);

for (const key of Object.keys(props)) {
  if (key !== "note") {
    getEntity(key);
    if (entity.value) {
      break;
    }
  }
}

function processEntity(name: string): void {
  // TODO: add search value to the links and review other ocurrences of the same problem
  if (entity.value) {
    if (name === "target") {
      icon.value = "mdi-target";
      link.value = `/projects/${route.params.project_id}/targets`;
      value.value = entity.value.target;
    } else if (name === "execution" || name === "task") {
      icon.value = "mdi-play";
      if (name === "execution") {
        link.value = `/projects/${route.params.project_id}/scans/${entity.value.task}`;
        value.value = entity.value.configuration.name;
      } else {
        link.value = `/projects/${route.params.project_id}/scans/${entity.value.id}`;
        value.value = entity.value.configuration
          ? entity.value.configuration.name
          : entity.value.process.name;
      }
    } else {
      icon.value =
        enums.findings[
          name === "osint"
            ? name.toUpperCase()
            : `${name.charAt(0).toUpperCase()}${name.slice(1)}`
        ].icon;
      link.value = `/projects/${route.params.project_id}/findings`;
      const fields = [
        "name",
        "title",
        "ip",
        "port",
        "path",
        "data",
        "email",
        "username",
        "secret",
      ];
      for (const field of fields) {
        if (field in entity.value && entity[field]) {
          value.value = entity[field];
          break;
        }
      }
    }
  }
}

function getEntity(name: string): void {
  if (props.note && props.note[name] !== null) {
    useApi(
      `/api/${name.charAt(name.length - 1) === "y" ? name.substring(0, name.length - 1) + "ies" : name !== "osint" ? name + "s" : name}/`,
      true,
    )
      .get(props.note[name])
      .then((response) => {
        entity.value = response;
        processEntity(name);
      });
  } else if (props[name]) {
    entity.value = props[name];
    processEntity(name);
  }
}
</script>
