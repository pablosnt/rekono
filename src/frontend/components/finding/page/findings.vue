<template>
  <v-tabs
    v-model="tab"
    align-tabs="center"
    fixed-tabs
    @update:model-value="tabChange()"
  >
    <v-tab
      value="osint"
      text="OSINT"
      :prepend-icon="enums.findings.OSINT.icon"
      color="red-darken-2"
    />
    <v-tab
      value="vulnerabilities"
      text="Vulnerabilities"
      :prepend-icon="enums.findings.Vulnerability.icon"
      color="red-darken-2"
    />
  </v-tabs>
  <Dataset
    v-if="filtering.length > 0"
    ref="dataset"
    :key="forceUpdate"
    :api="tabs[tab].api"
    :icon="tabs[tab].icon"
    :filtering="filtering"
    :expand-filters="expandFilters"
    :default-parameters="defaultParameters"
    :empty-head="tabs[tab].emptyHead"
    :empty-text="tabs[tab].emptyText"
    @load-data="(data) => (findings = data)"
    @expand-filters="(value) => (expandFilters = value)"
  >
    <template #data>
      <v-tabs-window v-model="tab">
        <v-container fluid>
          <v-row dense>
            <v-col v-for="finding in findings" :key="finding.id" cols="6">
              <v-tabs-window-item value="osint">
                <FindingShowOsint
                  :api="tabs[tab].api"
                  :finding="finding"
                  :defectdojo="defectdojo"
                  :defectdojo-settings="defectdojoSettings"
                  :hacktricks="hacktricks"
                  @reload="dataset.loadData(false)"
                />
              </v-tabs-window-item>
              <v-tabs-window-item value="vulnerabilities">
                <FindingShowVulnerability
                  :api="tabs[tab].api"
                  :finding="finding"
                  :defectdojo="defectdojo"
                  :defectdojo-settings="defectdojoSettings"
                  :hacktricks="hacktricks"
                  @reload="dataset.loadData(false)"
                />
              </v-tabs-window-item>
            </v-col>
          </v-row>
        </v-container>
      </v-tabs-window>
    </template>
  </Dataset>
</template>

<script setup lang="ts">
const props = defineProps({
  defaultParameters: Object,
  globalFiltering: Array,
  triageFiltering: Array,
  defectdojo: Object,
  defectdojoSettings: Object,
  hacktricks: Object,
  task: {
    type: Object,
    required: false,
    default: null,
  },
  execution: {
    type: Object,
    required: false,
    default: null,
  },
  matchPath: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const route = useRoute();
const router = useRouter();
const enums = useEnums();
const filters = useFilters();

const forceUpdate = ref(1);
const expandFilters = ref(false);
const dataset = ref(null);
const findings = ref([]);

const tab = ref(
  route.query.tab &&
    ["osint", "vulnerabilities"].includes(
      route.query.tab.toString().toLowerCase(),
    )
    ? route.query.tab.toString().toLowerCase()
    : "osint",
);

const tabs = ref({
  osint: {
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
    triage: true,
    ordering: ["id", "data", "data_type", "source"],
  },
  vulnerabilities: {
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
                  port: name,
                  ordering: "port",
                },
                true,
              )
              .then((response) => {
                definition.collection = response.items;
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
        fieldValue: "name",
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
    triage: true,
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
  },
});
const filtering = ref([]);
buildFiltering();

function buildFiltering() {
  filters.build(tabs.value[tab.value].filtering).then((tabFilters) => {
    filters
      .build([
        {
          type: "autocomplete",
          label: "Sort",
          icon: "mdi-sort",
          cols: 2,
          collection: tabs.value[tab.value].ordering,
          fieldValue: "id",
          fieldTitle: "name",
          key: "ordering",
          defaultValue: "-id",
        },
      ])
      .then((orderFilters) => {
        filtering.value = tabFilters
          .concat(props.globalFiltering)
          .concat(props.triageFiltering)
          .concat(orderFilters);
      });
  });
}

function tabChange() {
  buildFiltering();
  forceUpdate.value++;
  if (dataset.value) {
    findings.value = [];
    dataset.value.loadData(true);
  }
  if (props.matchPath) {
    router.replace({
      query: Object.assign({}, route.query, { tab: tab.value }),
    });
  }
}
</script>
