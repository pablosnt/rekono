<template>
  <MenuProject>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :default-parameters="{ project: route.params.project_id }"
      :add="ReportDialog"
      icon="mdi-file-document-multiple"
      empty-head="No Reports"
      empty-text="There are no reports yet. Create your first one"
      @load-data="(data) => (reports = data)"
    >
      <!--
           todo: Fix date
           todo: Sometimes, multiple reports are created with the same ID, and then you can't remove or download them
           todo: PDF reports are not generated. Dialog gets stucked
           todo: Allow filtering by completed tasks in autocomplete?   
        -->
      <template #data>
        <v-row dense>
          <v-col v-for="report in reports" :key="report.id" cols="4">
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
                    :icon="
                      enums.reportFormats[report.format.toLowerCase()].icon
                    "
                    :color="enums.reportStatuses[report.status].color"
                  />
                  <v-tooltip activator="parent" :text="report.status" />
                </v-btn>
              </template>
              <template #append>
                <v-chip
                  v-if="report.target && !report.task"
                  class="mr-2"
                  prepend-icon="mdi-target"
                  color="red"
                  link
                  :text="report.target.target"
                  :to="`/projects/${route.params.project_id}/targets/${report.target.id}`"
                />
                <v-chip
                  v-if="report.task"
                  class="mr-2"
                  prepend-icon="mdi-play-network"
                  color="red"
                  link
                  :text="
                    report.task.process
                      ? report.task.process.name
                      : `${report.task.configuration.tool.name} - ${report.task.configuration.name}`
                  "
                  :to="`/projects/${route.params.project_id}/targets/${report.task.id}`"
                />
                <UtilsOwner :entity="report" field="user" />
              </template>
              <v-card-actions>
                <ReportDownloadButton :api="api" :report="report" />
                <v-spacer />
                <UtilsButtonDelete
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
const ReportDialog = resolveComponent("ReportDialog");
const route = useRoute();
const user = userStore();
const enums = ref(useEnums());
const filters = useFilters();
const dataset = ref(null);
const reports = ref([]);
const api = useApi("/api/reports/", true, "Report");
const filtering = ref([]);
filters
  .build([
    {
      type: "autocomplete",
      label: "Target",
      icon: "mdi-target",
      cols: 2,
      request: useApi("/api/targets/", true).list({}, true),
      fieldValue: "id",
      fieldTitle: "target",
      key: "target",
      callback: (value, definitions) => {
        const tasks = filters.getDefinitionFromKey("task", definitions);
        if (value) {
          useApi("/api/tasks/", true)
            .list({ target: value }, true)
            .then((response) => {
              tasks.collection = response.items;
              tasks.disabled = false;
              filters.setValueFromQuery(tasks)
            });
        } else {
          tasks.collection = [];
          tasks.value = null;
          tasks.disabled = true;
        }
      },
    },
    {
      type: "autocomplete",
      label: "Scan",
      icon: "mdi-play-network",
      collection: [],
      fieldValue: "id",
      key: "task",

      disabled: true,
    },
    // todo: Format filter is not working for XML and PDF. It's returning 404
    {
      type: "autocomplete",
      label: "Format",
      icon: "mdi-file-document",
      cols: 2,
      collection: Object.entries(enums.value.reportFormats).map(([k, v]) => {
        v.id = k.toLowerCase();
        v.name = k.toUpperCase();
        return v;
      }),
      fieldValue: "id",
      fieldTitle: "name",
      key: "format",
    },
    {
      type: "autocomplete",
      label: "Status",
      icon: "mdi-check-decagram",
      cols: 2,
      collection: filters.collectionFromEnum(enums.value.reportStatuses),
      fieldValue: "name",
      fieldTitle: "name",
      key: "status",
    },
    {
      type: "switch",
      label: "Mine",
      color: "blue",
      cols: 1,
      key: "user",
      trueValue: user.user,
      falseValue: null,
    },
    {
      type: "autocomplete",
      label: "Sort",
      icon: "mdi-sort",
      cols: 2,
      collection: ["id", "target", "task", "status", "format", "date"],
      fieldValue: "id",
      fieldTitle: "name",
      key: "ordering",
      defaultValue: "id",
    },
  ])
  .then((results) => (filtering.value = results));
</script>
