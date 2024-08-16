<template>
  <MenuProject>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :default-parameters="{ project: route.params.project_id }"
      ordering="id"
      :add="DialogReport"
      icon="mdi-file-document-multiple"
      empty-head="No Reports"
      empty-text="There are no reports yet. Create your first one"
      @load-data="(data) => (reports = data)"
    >
      <template #data>
        <v-row dense>
          <v-col v-for="report in reports" :key="report.id" cols="6">
            <v-card
              :title="report.format.toUpperCase()"
              :subtitle="
                report.date ? new Date(report.date).toUTCString() : undefined
              "
              elevation="3"
              class="mx-auto"
              density="compact"
            >
              <template #prepend>
                <v-btn hover variant="text" icon>
                  <v-icon
                    :icon="enums.reports[report.format.toLowerCase()].icon"
                    :color="
                      report.status === 'Ready'
                        ? 'green'
                        : report.status === 'Error'
                          ? 'red'
                          : 'yellow'
                    "
                  />
                  <v-tooltip activator="parent" :text="report.status" />
                </v-btn>
              </template>
              <template #append>
                <div v-if="report.target || report.task">
                  <v-chip
                    v-if="report.target"
                    prepend-icon="mdi-target"
                    color="red"
                    link
                    :text="report.target.target"
                    :to="`/projects/${route.params.project_id}/targets/${report.target.id}`"
                  />
                  <v-chip
                    v-if="report.task"
                    prepend-icon="mdi-play-network"
                    color="red"
                    link
                    :text="
                      report.task.process
                        ? report.task.process.name
                        : report.task.configuration.name
                    "
                    :to="`/projects/${route.params.project_id}/targets/${report.task.id}`"
                  />
                </div>
                <div v-if="!report.target && !report.task">
                  <ButtonReportDownload :api="api" :report="report" />
                  <ButtonDelete
                    :id="report.id"
                    :api="api"
                    :text="`Report '${report.id}' will be removed`"
                    icon="mdi-trash-can"
                    @completed="dataset.loadData(false)"
                  />
                </div>
              </template>
              <v-card-actions v-if="report.target || report.task">
                <v-spacer />
                <ButtonReportDownload :api="api" :report="report" />
                <ButtonDelete
                  :id="report.id"
                  :api="api"
                  :text="`Report '${report.id}' will be removed`"
                  icon="mdi-trash-can"
                  @completed="dataset.loadData(false)"
                />
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </Dataset>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const DialogReport = resolveComponent("DialogReport");
const route = useRoute();
const enums = useEnums();
const dataset = ref(null);
const reports = ref([]);
const api = useApi("/api/reports/", true, "Report");
const filtering = ref([]);
// TODO
</script>
