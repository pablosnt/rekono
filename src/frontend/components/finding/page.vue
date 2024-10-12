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
      value="assets"
      text="Assets"
      :prepend-icon="enums.findings.Host.icon"
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
        <v-tabs-window-item value="osint">
          <FindingShowOsint
            :api="api"
            :findings="findings"
            :defectdojo="defectdojo"
            :defectdojo-settings="defectdojoSettings"
            :hacktricks="hacktricks"
            @reload="dataset.loadData(false)"
          />
        </v-tabs-window-item>
        <v-tabs-window-item value="assets">
          <FindingShowAssets
            :api="api"
            :findings="findings"
            :defectdojo="defectdojo"
            :defectdojo-settings="defectdojoSettings"
            :hacktricks="hacktricks"
            @reload="dataset.loadData(false)"
          />
        </v-tabs-window-item>
        <v-tabs-window-item value="vulnerabilities">
          <FindingShowVulnerabilities
            :api="api"
            :findings="findings"
            :defectdojo="defectdojo"
            :defectdojo-settings="defectdojoSettings"
            :hacktricks="hacktricks"
            @reload="dataset.loadData(false)"
          />
        </v-tabs-window-item>
      </v-tabs-window>
    </template>
  </Dataset>
</template>

<script setup lang="ts">
const props = defineProps({
  execution: {
    type: Number,
    required: false,
    default: null,
  },
  matchPath: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const user = userStore();
const route = useRoute();
const router = useRouter();
const enums = useEnums();
const filters = useFilters();
const dataset = ref(null);
const forceUpdate = ref(1);
const expandFilters = ref(false);
const findings = ref([]);
const tab = ref(
  route.query.tab &&
    ["osint", "assets", "vulnerabilities"].includes(
      route.query.tab.toString().toLowerCase(),
    )
    ? route.query.tab.toString().toLowerCase()
    : "osint",
);
const defaultParameters = ref(
  props.execution
    ? { executions: [props.execution] }
    : route.params.task_id
      ? { task: route.params.task_id }
      : { project: route.params.project_id },
);

const hacktricks = ref(null);
const defectdojo = ref(null);
const defectdojoSettings = ref(null);
const integrationApi = useApi("/api/integrations/", true);
integrationApi.get(3).then((response) => (hacktricks.value = response));
integrationApi.get(1).then((response) => (defectdojo.value = response));
useApi("/api/defect-dojo/settings/", true)
  .get(1)
  .then((response) => (defectdojoSettings.value = response));

const triageFiltering = [
  {
    cols: 3,
    type: "autocomplete",
    label: "Triage Status",
    icon: enums.triage.Untriaged.icon,
    collection: filters.collectionFromEnum(enums.triage),
    fieldValue: "name",
    fieldTitle: "name",
    key: "triage_status__in",
    defaultValue: ["Untriaged", "True Positive", "Won't Fix"],
    multiple: true,
  },
  {
    type: "switch",
    label: "My Triage",
    color: "blue",
    cols: 1,
    key: "triage_by",
    trueValue: user.user,
    falseValue: null,
    isAuditor: true,
  },
];
const globalFiltering = filters.build([
  {
    type: "autocomplete",
    cols: 2,
    label: "Target",
    icon: "mdi-target",
    request: useApi("/api/targets/", true).list(
      { project: route.params.project_id, ordering: "target" },
      true,
    ),
    fieldValue: "id",
    fieldTitle: "target",
    key: "target",
    skip: props.execution !== null || route.params.task_id,
    callback: (value, definitions) => {
      const task = filters.getDefinitionFromKey("task", definitions);
      const host = filters.getDefinitionFromKey("host", definitions);
      if (value) {
        task.disabled = false;
        useApi("/api/tasks/", true)
          .list(
            {
              project: route.params.project_id,
              target: value,
              ordering: "-id",
            },
            true,
          )
          .then((response) => {
            task.collection = response.items;
          });
        if (host) {
          useApi("/api/hosts/", true)
            .list(
              {
                project: route.params.project_id,
                target: value,
                ordering: "address",
              },
              true,
            )
            .then((response) => (host.collection = response.items));
        }
      } else {
        task.disabled = true;
        task.value = null;
        task.collection = [];
        if (host) {
          host.request.then((response) => (host.collection = response.items));
        }
      }
    },
  },
  {
    type: "autocomplete",
    cols: 3,
    label: "Scan",
    icon: "mdi-play-network",
    collection: [],
    fieldValue: "id",
    key: "task",
    skip: props.execution !== null || route.params.task_id,
    disabled: true,
  },
  {
    type: "autocomplete",
    cols: 2,
    label: "Tool",
    icon: "mdi-rocket",
    enforceIcon: true,
    request: useApi("/api/tools/", true).list({ ordering: "name" }, true),
    fieldValue: "id",
    fieldTitle: "name",
    key: "tool",
    skip: props.execution !== null,
  },
  {
    type: "switch",
    label: "Fixed",
    color: "green",
    cols: 1,
    key: "is_fixed",
    trueValue: true,
    falseValue: false,
    defaultValue: false,
    callback: (value, definitions) => {
      const auto = filters.getDefinitionFromKey("auto_fixed", definitions);
      const mine = filters.getDefinitionFromKey("fixed_by", definitions);
      auto.disabled = value === false;
      mine.disabled = value === false;
      if (!value) {
        auto.value = null;
        mine.value = null;
      }
    },
  },
  {
    type: "switch",
    label: "Auto Fixed",
    color: "green",
    cols: 1,
    key: "auto_fixed",
    trueValue: true,
    falseValue: null,
    disabled: true,
    callback: (value, definitions) => {
      const mine = filters.getDefinitionFromKey("fixed_by", definitions);
      mine.disabled = value !== null;
      if (mine.disabled) {
        mine.value = null;
      }
    },
  },
  {
    type: "switch",
    label: "My Fixes",
    color: "blue",
    cols: 1,
    key: "fixed_by",
    trueValue: user.user,
    falseValue: null,
    isAuditor: true,
    disabled: true,
    callback: (value, definitions) => {
      const mine = filters.getDefinitionFromKey("auto_fixed", definitions);
      mine.disabled = value !== null;
      if (mine.disabled) {
        mine.value = null;
      }
    },
  },
]);
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
  assets: {
    api: useApi("/api/hosts/", true),
    icon: enums.findings.Host.icon,
    emptyHead: "No assets found",
    emptyText:
      "Run some enumeration tool to identify some assets exposed by your targets",
    filtering: [
      {
        cols: 2,
        type: "autocomplete",
        label: "OS",
        icon: enums.osType.Other.icon,
        collection: filters.collectionFromEnum(enums.osType),
        fieldValue: "name",
        fieldTitle: "name",
        key: "os_type",
      },
    ],
    triage: false,
    ordering: ["id", "host", "address", "os_type"],
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
const filtering = ref(buildFiltering());

function buildFiltering() {
  return filters
    .build(tabs.value[tab.value].filtering)
    .concat(globalFiltering)
    .concat(tabs.value[tab.value].triage ? filters.build(triageFiltering) : [])
    .concat(
      filters.build([
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
      ]),
    );
}

function tabChange() {
  filtering.value = buildFiltering();
  forceUpdate.value++;
  if (dataset.value) {
    findings.value = [];
    dataset.value.loadData(true);
  }
  if (props.matchPath) {
    router.replace({ query: { tab: tab.value } });
  }
}
</script>
