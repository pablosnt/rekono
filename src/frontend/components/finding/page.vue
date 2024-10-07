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
    v-if="api"
    ref="dataset"
    :api="api"
    ordering="-id"
    :icon="tabs[tab].icon"
    :filtering="filtering"
    :default-parameters="defaultParameters"
    :empty-head="tabs[tab].emptyHead"
    :emtpy-text="tabs[tab].emptyText"
    @load-data="(data) => (findings = data)"
  >
    <template #data>
      <v-tabs-window v-model="tab">
        <v-tabs-window-item value="osint">
          <FindingComponentOsint
            :api="api"
            :findings="findings"
            :defectdojo="defectdojo"
            :defectdojo-settings="defectdojoSettings"
            :hacktricks="hacktricks"
            @reload="dataset.loadData(false)"
          />
        </v-tabs-window-item>
        <v-tabs-window-item value="assets">
          <FindingComponentAssets
            :api="api"
            :findings="findings"
            :defectdojo="defectdojo"
            :defectdojo-settings="defectdojoSettings"
            :hacktricks="hacktricks"
            @reload="dataset.loadData(false)"
          />
        </v-tabs-window-item>
        <v-tabs-window-item value="vulnerabilities">
          <FindingComponentVulnerabilities
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
const route = useRoute();
const router = useRouter();
const enums = useEnums();
const dataset = ref(null);
const findings = ref([]);

// TODO: Filtering
const tabs = ref({
  osint: {
    endpoint: "/api/osint/",
    icon: enums.findings.OSINT.icon,
    emptyHead: "No OSINT findings",
    emptyText:
      "Run some OSINT tool to identify some OSINT information about your targets",
    filtering: [],
  },
  assets: {
    endpoint: "/api/osint/",
    icon: enums.findings.Host.icon,
    emptyHead: "No assets found",
    emptyText:
      "Run some enumeration tool to identify some assets exposed by your targets",
    filtering: [],
  },
  vulnerabilities: {
    endpoint: "/api/osint/",
    icon: enums.findings.Vulnerability.icon,
    emptyHead: "No vulnerabilities found",
    emptyText: "Run some vulnerability scan to identify some in your assets",
    filtering: [],
  },
});
// TODO
const globalFiltering = [];

const tab = ref(
  route.query.tab &&
    ["osint", "assets", "vulnerabilities"].includes(
      route.query.tab.toString().toLowerCase(),
    )
    ? route.query.tab.toString().toLowerCase()
    : "osint",
);
const api = computed(() => {
  return useApi(tabs.value[tab.value].endpoint, true);
});
const filtering = computed(() => {
  return globalFiltering.concat(tabs.value[tab.value].filtering);
});

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

function tabChange() {
  if (props.matchPath) {
    router.replace({ query: { tab: tab.value } });
  }
  findings.value = [];
  dataset.value.loadData(true);
}
</script>
