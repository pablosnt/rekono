<template>
  <MenuProject>
    <FindingTab>
      <!-- TODO: All findings must be loaded from the same page to show them from Task page -->
      <!-- TODO: Keep filters between tabs (implementation depends on the previous todo) -->
      <Dataset
        ref="dataset"
        :api="api"
        ordering="-id"
        :icon="enums.findings.OSINT"
        :filtering="filtering"
        :default-parameters="{ project: route.params.project_id }"
        empty-head="No OSINT findings"
        empty-text="Run some OSINT tool to identify some OSINT information about your targets"
        @load-data="(data) => (osint = data)"
      >
        <template #data>
          <!-- TODO: Create utils component to include common components like container, row, etc -->
          <v-container fluid>
            <v-row dense>
              <v-col v-for="finding in osint" :key="finding.id" cols="6">
                <v-card :title="finding.data" :subtitle="finding.source">
                  <!-- TODO: Common compontent for findings: links, triage (only for some), fix, etc -->
                  <template #prepend>
                    <v-btn hover icon variant="text" @click.prevent.stop>
                      <v-icon
                        :icon="enums.osintTypes[finding.data_type].icon"
                        color="red"
                      />
                      <v-tooltip activator="parent" :text="finding.data_type" />
                    </v-btn>
                  </template>
                  <template #append>
                    <FindingLinks
                      :finding="finding"
                      :defectdojo="defectdojo"
                      :defectdojo-settings="defectdojoSettings"
                      :hacktricks="hacktricks"
                    />
                  </template>
                  <!-- <template #text>
                    TODO: Counters of detections per tools
                  </template> -->
                  <v-card-actions>
                    <!-- TODO: This button is not shown? -->
                    <FindingFix
                      :api="api"
                      :finding="finding"
                      @change="dataset.loadData(false)"
                    />
                    <v-spacer />
                    <FindingTriageButton
                      :api="api"
                      :finding="finding"
                      @change="dataset.loadData(false)"
                    />
                    <v-btn
                      v-if="['IP', 'Domain'].includes(finding.data_type)"
                      hover
                      icon
                      variant="text"
                      @click="
                        api
                          .create({}, finding.id, 'target/')
                          .then(() =>
                            navigateTo(
                              `/projects/${route.params.project_id}/targets`,
                            ),
                          )
                      "
                    >
                      <v-icon icon="mdi-target" color="red" />
                      <v-tooltip activator="parent" text="Create target" />
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </template>
      </Dataset>
    </FindingTab>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
const enums = useEnums();
const dataset = ref(null);
const osint = ref([]);
const api = useApi("/api/osint/", true);

// TODO: Keep common filters between tabs
const filtering = ref([]);

// TODO: Keep this between tabs. Move this to a composable?
const integrationApi = useApi("/api/integrations/", true);
const defectdojo = ref(null);
const hacktricks = ref(null);
integrationApi.get(1).then((response) => (defectdojo.value = response));
integrationApi.get(3).then((response) => (hacktricks.value = response));
const defectdojoSettings = ref(null);
useApi("/api/defect-dojo/settings/", true)
  .get(1)
  .then((response) => (defectdojoSettings.value = response));
</script>
