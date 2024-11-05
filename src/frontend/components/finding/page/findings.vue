<template>
  <DatasetSharedTabs
    :tabs="tabs"
    :default-parameters="defaultParameters"
    :default-properties="{
      defectdojo: defectdojo,
      defectdojoSettings: defectdojoSettings,
      hacktricks: hacktricks,
    }"
    :global-filtering="globalFiltering.concat(triageFiltering)"
    entity="finding"
    :match-query="matchQuery"
  />
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

const tabs = ref({
  osint: {
    text: "OSINT",
    component: resolveComponent("FindingShowOsint"),
    api: useApi("/api/osint/", true),
    icon: enums.findings.OSINT.icon,
    emptyHead: "No OSINT findings",
    emptyText:
      "Run some OSINT tool to identify some OSINT information about your targets",
    filtering: [
      {
        cols: 2,
        type: "autocomplete",
        label: "Data Type",
        icon: "mdi-tag-multiple",
        collection: filters.collectionFromEnum(enums.osintTypes),
        fieldValue: "name",
        fieldTitle: "name",
        key: "data_type",
      },
    ],
    ordering: ["id", "data", "data_type", "source"],
  },
  vulnerabilities: {
    text: "Vulnerabilities",
    component: resolveComponent("FindingShowVulnerability"),
    api: useApi("/api/vulnerabilities/", true),
    icon: enums.findings.Vulnerability.icon,
    emptyHead: "No vulnerabilities found",
    emptyText: "Run some vulnerability scan to identify some in your assets",
    filtering: [
      {
        type: "autocomplete",
        cols: 2,
        label: "Host",
        icon: enums.findings.Host.icon,
        request: useApi("/api/hosts/", true).list(
          { project: route.params.project_id, ordering: "address" },
          true,
        ),
        fieldValue: "id",
        fieldTitle: "address",
        key: "host",
        callback: (value, definitions) => {
          const definition = filters.getDefinitionFromKey("port", definitions);
          if (value) {
            definition.disabled = false;
            useApi("/api/ports/", true)
              .list(
                {
                  project: route.params.project_id,
                  host: value,
                  ordering: "port",
                },
                true,
              )
              .then((response) => {
                definition.collection = response.items;
                filters.setValueFromQuery(definition);
              });
          } else {
            definition.disabled = true;
            definition.value = null;
            definition.collection = [];
          }
        },
      },
      {
        type: "autocomplete",
        cols: 2,
        label: "Port",
        icon: enums.findings.Port.icon,
        collection: [],
        fieldValue: "id",
        fieldTitle: "port",
        key: "port",
        disabled: true,
        callback: (value, definitions) => {
          const definition = filters.getDefinitionFromKey(
            "technology",
            definitions,
          );
          if (value) {
            definition.disabled = false;
            useApi("/api/technologies/", true)
              .list(
                {
                  project: route.params.project_id,
                  port: value,
                  ordering: "port",
                },
                true,
              )
              .then((response) => {
                definition.collection = response.items;
                filters.setValueFromQuery(definition);
              });
          } else {
            definition.disabled = true;
            definition.value = null;
            definition.collection = [];
          }
        },
      },
      {
        type: "autocomplete",
        cols: 2,
        label: "Technology",
        icon: enums.findings.Technology.icon,
        collection: [],
        fieldValue: "id",
        fieldTitle: "name",
        key: "technology",
        disabled: true,
      },
      {
        cols: 2,
        type: "autocomplete",
        label: "Severity",
        icon: "mdi-fire",
        collection: filters.collectionFromEnum(enums.severity),
        fieldValue: "id",
        fieldTitle: "name",
        key: "severity",
      },
      {
        type: "text",
        label: "CVE",
        icon: "mdi-identifier",
        cols: 2,
        key: "cve",
      },
      {
        type: "text",
        label: "CWE",
        icon: "mdi-tag",
        cols: 2,
        key: "cwe",
      },
      {
        type: "switch",
        label: "Trending",
        color: "red",
        cols: 1,
        key: "trending",
        trueValue: true,
        falseValue: null,
      },
    ],
    ordering: [
      "id",
      "technology",
      "port",
      "name",
      "severity",
      "cve",
      "cwe",
      "osvdb",
    ],
    defaultOrdering: '-severity'
  },
});
</script>
