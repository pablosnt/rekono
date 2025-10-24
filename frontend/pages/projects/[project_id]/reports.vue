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
    >
      <!--
           TODO: Fix date
           TODO: Sometimes, multiple reports are created with the same ID, and then you can't remove or download them
           TODO: PDF reports are not generated. Dialog gets stucked
           TODO: Allow filtering by completed tasks in autocomplete?   
        -->
      <template #item="{ item }">
        <v-card
          :title="item.format.toUpperCase()"
          :subtitle="
            item.date
              ? new Date(item.date).toLocaleString(undefined, { hour12: false })
              : undefined
          "
          elevation="3"
          class="mx-auto"
          density="compact"
        >
          <template #prepend>
            <BaseButton
              hover
              :icon="enums.reportFormats[item.format.toLowerCase()].icon"
              :icon-color="enums.reportStatuses[item.status].color"
              :tooltip="item.status"
            />
          </template>
          <template #append>
            <v-chip
              v-if="item.target && !item.task"
              class="mr-2"
              prepend-icon="mdi-target"
              color="red"
              link
              :text="item.target.target"
              :to="`/projects/${route.params.project_id}/targets/${item.target.id}`"
            />
            <v-chip
              v-if="item.task"
              class="mr-2"
              prepend-icon="mdi-play-network"
              color="red"
              link
              :text="
                item.task.process
                  ? item.task.process.name
                  : `${item.task.configuration.tool.name} - ${item.task.configuration.name}`
              "
              :to="`/projects/${route.params.project_id}/targets/${item.task.id}`"
            />
            <UtilsOwner :entity="item" field="user" />
          </template>
          <v-card-actions>
            <BaseButton
              variant="text"
              :disabled="item.status !== 'Ready'"
              hover
              icon="mdi-download"
              icon-color="primary"
              tooltip="Download"
              @click="api.download(item.id, 'download/', {})"
            />
            <v-spacer />
            <UtilsDeleteButton
              :id="item.id"
              :api="api"
              :text="`Report '${item.id}' will be removed`"
              icon="mdi-trash-can"
              @completed="dataset.loadData(false)"
            />
          </v-card-actions>
        </v-card>
      </template>
    </Dataset>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const ReportDialog = resolveComponent("ReportDialog");
const route = useRoute();
const user = userStore();
const enums = useEnums();
const filters = useFilters();
const dataset = ref(null);
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
              filters.setValueFromQuery(tasks);
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
    // TODO: Format filter is not working for XML and PDF. It's returning 404
    {
      type: "autocomplete",
      label: "Format",
      icon: "mdi-file-document",
      cols: 2,
      collection: Object.entries(enums.reportFormats).map(([k, v]) => {
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
      collection: filters.collectionFromEnum(enums.reportStatuses),
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
