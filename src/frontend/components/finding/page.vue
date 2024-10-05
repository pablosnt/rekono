<template>
  <Dataset
    v-if="api"
    ref="dataset"
    :api="api"
    ordering="-id"
    :icon="icon"
    :filtering="filtering"
    :default-parameters="defaultParameters"
    :empty-head="emptyHead"
    :emtpy-text="emptyText"
    @load-data="(data) => (findings = data)"
  >
    <template #data>
      <v-tabs
        v-model="tab"
        align-tabs="center"
        fixed-tabs
        @update:model-value="tabChange()"
      >
        <v-tab
          :value="1"
          text="OSINT"
          :prepend-icon="enums.findings.OSINT.icon"
          color="red-darken-2"
        />
        <v-tab
          :value="2"
          text="Assets"
          :prepend-icon="enums.findings.Host.icon"
          color="red-darken-2"
        />
        <v-tab
          :value="3"
          text="Vulnerabilities"
          :prepend-icon="enums.findings.Vulnerability.icon"
          color="red-darken-2"
        />
      </v-tabs>
      <v-tabs-window v-model="tab">
        <v-tabs-window-item :value="1">
          <FindingComponentOsint
            :api="api"
            :findings="findings"
            :defectdojo="defectdojo"
            :defectdojo-settings="defectdojoSettings"
            :hacktricks="hacktricks"
            @reload="dataset.loadData(false)"
          />
        </v-tabs-window-item>
        <v-tabs-window-item :value="2">
          <FindingComponentOsint
            :api="api"
            :findings="findings"
            :defectdojo="defectdojo"
            :defectdojo-settings="defectdojoSettings"
            :hacktricks="hacktricks"
            @reload="dataset.loadData(false)"
          />
        </v-tabs-window-item>
        <v-tabs-window-item :value="3">
          <FindingComponentOsint
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
  defaultTab: {
    type: Number,
    required: false,
    default: 1,
  },
  // TODO: keep path updated with current tab
  matchPath: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const route = useRoute();
const enums = useEnums();
const tab = ref(props.defaultTab);

const dataset = ref(null);
const findings = ref([]);

const osintApi = useApi("/api/osint/", true);
const hostsApi = useApi("/api/hosts/", true);
const vulnsApi = useApi("/api/vulnerabilities/", true);
const api = ref(null);

const icon = ref(null);
const emptyHead = ref(null);
const emptyText = ref(null);

// TODO: Keep global filters between tabs
const globalFiltering = [];
const filtering = ref([]);
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

tabChange();

function tabChange() {
  if (tab.value === 1) {
    api.value = osintApi;
    icon.value = enums.findings.OSINT.icon;
    emptyHead.value = "No OSINT findings";
    emptyText.value =
      "Run some OSINT tool to identify some OSINT information about your targets";
  } else if (tab.value === 2) {
    api.value = hostsApi;
    icon.value = enums.findings.Host.icon;
    emptyHead.value = "No assets found";
    emptyText.value =
      "Run some enumeration tool to identify some assets exposed by your targets";
  } else if (tab.value === 3) {
    api.value = vulnsApi;
    icon.value = enums.findings.Vulnerability.icon;
    emptyHead.value = "No vulnerabilities found";
    emptyText.value =
      "Run some vulnerability scan to identify some in your assets";
  }
  if (dataset.value) {
    dataset.value.loadData(true);
  }
}
</script>
