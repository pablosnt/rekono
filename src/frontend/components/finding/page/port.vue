<template>
  <v-card
    v-if="port !== null && host !== null"
    class="pa-6"
    :title="`${port.protocol} ${port.port} ${port.service ? port.service : ''}`"
    :subtitle="host.address"
    :prepend-icon="portsUtils.getIcon(port.port)"
    variant="text"
  >
    <template #append>
      <v-chip class="mr-5" :color="enums.portStatus[port.status].color">{{
        port.status
      }}</v-chip>
      <v-btn variant="text">
        <v-chip
          v-if="exposure"
          :text="exposure"
          prepend-icon="mdi-clock-alert"
          color="red"
        />
        <v-tooltip activator="parent" text="Exposure time" />
      </v-btn>
      <FindingToolCounter
        class="mr-3"
        :finding="port"
        @exposure="(value) => (exposure = value)"
      />
      <FindingFix :api="api" :finding="port" asset-syntax @change="getPort()" />
      <NoteButton :port="port" :project="route.params.project_id" />
      <UtilsCounter
        class="ml-2"
        :collection="port.notes"
        tooltip="Notes"
        icon="mdi-notebook"
        :link="`/projects/${route.params.project_id}/notes`"
        color="indigo-darken-1"
        new-tab
      />
      <FindingLinks
        :finding="port"
        :defectdojo="defectdojo"
        :defectdojo-settings="defectdojoSettings"
        :hacktricks="hacktricks"
      />
      <UtilsCounter
        icon="mdi-ladybug"
        size="x-large"
        :collection="port.vulnerability"
        :link="`/projects/${route.params.project_id}/findings?tab=vulnerabilities&host=${port.host}&port=${port.id}`"
        tooltip="Vulnerabilities"
        show-zero
      />
    </template>
    <template #text>
      <DatasetSharedTabs
        :tabs="tabs"
        :default-parameters="Object.assign({}, defaultParameters, { port: port.id })"
        :default-properties="{
          defectdojo: defectdojo,
          defectdojoSettings: defectdojoSettings,
          hacktricks: hacktricks,
          host: port.host
        }"
        :global-filtering="globalFiltering"
        entity="finding"
        :match-query="matchQuery"
      />
    </template>
  </v-card>
</template>

<script setup lang="ts">
defineProps({
  defaultParameters: Object,
  globalFiltering: Array,
  triageFiltering: Array,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
  matchQuery: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const route = useRoute();
const enums = useEnums();
const filters = useFilters();
const portsUtils = usePorts();
// TODO: Apply asset syntax to filters
const exposure = ref(null);
const api = useApi("/api/ports/", true);
const host = ref(null);
const port = ref(null);
getPort();

const tabs = ref({
  paths: {
    text: "Paths",
    component: resolveComponent("FindingShowPath"),
    api: useApi("/api/paths/", true),
    icon: enums.findings.Path.icon,
    emptyHead: "No paths found",
    emptyText: "Run some service discovery tool to detect your first one",
    filtering: [
      {
        cols: 2,
        type: "autocomplete",
        label: "Type",
        icon: "mdi-tag",
        collection: filters.collectionFromEnum(enums.osintTypes),
        fieldValue: "name",
        fieldTitle: "name",
        key: "type",
      },
    ],
    ordering: ["id", "path", "status", "type"],
  },
  technologies: {
    text: "Technologies",
    component: resolveComponent("FindingShowTechnology"),
    api: useApi("/api/technologies/", true),
    icon: enums.findings.Technology.icon,
    emptyHead: "No technologies found",
    emptyText: "Run some service discovery tool to detect your first one",
    filtering: [],
    ordering: ["id", "name", "version"],
  },
});

function getPort() {
  api.get(route.params.port_id).then((response) => {
    port.value = response;
    if (host.value === null) {
      useApi("/api/hosts/", true)
        .get(port.value.host)
        .then((hostResponse) => (host.value = hostResponse));
    }
  });
}
</script>
