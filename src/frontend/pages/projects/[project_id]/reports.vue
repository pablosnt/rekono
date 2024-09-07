<template>
  <MenuProject>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :default-parameters="{ project: route.params.project_id }"
      ordering="id"
      :add="ReportDialog"
      icon="mdi-file-document-multiple"
      empty-head="No Reports"
      empty-text="There are no reports yet. Create your first one"
      @load-data="(data) => (reports = data)"
      @new-filter="(key, value) => (key === 'target' ? getTasks(value) : null)"
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
                      : `${report.task.configuration.tool.name} - ${report.task.configuration.name}`
                  "
                  :to="`/projects/${route.params.project_id}/targets/${report.task.id}`"
                />
                <span v-if="report.target || report.task" class="me-2" />
                <UtilsChipOwner :entity="report" field="user" />
                <div v-if="!report.target && !report.task">
                  <ReportDownloadButton :api="api" :report="report" />
                  <UtilsButtonDelete
                    :id="report.id"
                    :api="api"
                    :text="`Report '${report.id}' will be removed`"
                    icon="mdi-trash-can"
                    @completed="dataset.loadData(false)"
                  />
                </div>
              </template>
              <v-card-actions v-if="report.target || report.task">
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
const dataset = ref(null);
const reports = ref([]);
const api = useApi("/api/reports/", true, "Report");
const filtering = ref([
  {
    type: "autocomplete",
    label: "Target",
    icon: "mdi-target",
    cols: 2,
    collection: [],
    fieldValue: "id",
    fieldTitle: "target",
    key: "target",
    value: null,
  },
  {
    type: "autocomplete",
    label: "Scan",
    icon: "mdi-play-network",
    collection: [],
    fieldValue: "id",
    fieldTitle: undefined,
    key: "task",
    value: null,
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
    value: null,
  },
  {
    type: "autocomplete",
    label: "Status",
    icon: "mdi-check-decagram",
    cols: 2,
    collection: Object.entries(enums.value.reportStatuses).map(([k, v]) => {
      v.name = k;
      return v;
    }),
    fieldValue: "name",
    fieldTitle: "name",
    key: "status",
    value: null,
  },
  {
    type: "switch",
    label: "Mine",
    color: "blue",
    cols: 1,
    key: "user",
    trueValue: user.user,
    falseValue: null,
    value: null,
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
    value: "id",
  },
]);

useApi("/api/targets/", true)
  .list({}, true)
  .then((response) => {
    filtering.value[0].collection = response.items;
  });

function getTasks(target) {
  if (target !== null) {
    useApi("/api/tasks/", true)
      .list({ target: target }, true)
      .then((response) => {
        filtering.value[1].collection = response.items;
        filtering.value[1].disabled = false;
      });
  } else {
    filtering.value[1].collection = [];
    filtering.value[1].value = null;
    filtering.value[1].disabled = true;
  }
}
</script>
