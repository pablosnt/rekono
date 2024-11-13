<template>
  <MenuProject>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :default-parameters="{ project: route.params.project_id }"
      :add="TargetDialog"
      icon="mdi-target"
      empty-head="No Targets"
      :empty-text="
        user.role === 'Reader'
          ? 'There are no targets'
          : 'Create your first target to start hacking'
      "
    >
      <template #item="{ item }">
        <v-card
          :title="item.target"
          :subtitle="item.type"
          elevation="2"
          class="mx-auto"
          density="compact"
          :prepend-icon="enums.targets[item.type].icon"
          :to="`/projects/${item.project}/targets/${item.id}/dashboard`"
        >
          <template #append>
            <UtilsCounter
              :collection="item.tasks"
              tooltip="Tasks"
              icon="mdi-play-network"
              :link="`/projects/${item.project}/scans`"
              color="red"
              new-tab
            />
            <UtilsCounter
              class="ml-2"
              :collection="item.reports"
              tooltip="Reports"
              icon="mdi-file-document-multiple"
              :link="`/projects/${item.project}/reports`"
              color="blue-grey-darken-1"
              new-tab
            />
            <UtilsCounter
              class="ml-2"
              :collection="item.notes"
              tooltip="Notes"
              icon="mdi-notebook"
              :link="`/projects/${item.project}/notes`"
              color="indigo-darken-1"
              new-tab
            />
            <!-- TODO: Link (Defect-Dojo) -->
          </template>
          <v-card-actions>
            <TaskButton v-if="project" :project="project" :target="item" />
            <v-spacer />
            <NoteButton :project="route.params.project_id" :target="item" />
            <ReportButton :project="route.params.project_id" :target="item" />
            <UtilsDeleteButton
              :id="item.id"
              :api="api"
              :text="`Target '${item.target}' will be removed`"
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
const user = userStore();
const enums = useEnums();
const route = useRoute();
const filters = useFilters();
const project = ref(null);
useApi("/api/projects/", true)
  .get(parseInt(route.params.project_id))
  .then((response) => (project.value = response));
const TargetDialog = resolveComponent("TargetDialog");
const dataset = ref(null);
const api = useApi("/api/targets/", true, "Target");
const filtering = ref([]);
filters
  .build([
    {
      type: "autocomplete",
      label: "Type",
      icon: "mdi-target",
      collection: filters.collectionFromEnum(enums.targets),
      fieldValue: "name",
      fieldTitle: "name",
      key: "type",
    },
    {
      type: "autocomplete",
      label: "Sort",
      icon: "mdi-sort",
      cols: 2,
      collection: ["id", "target", "type"],
      fieldValue: "id",
      fieldTitle: "name",
      key: "ordering",
      defaultValue: "id",
    },
  ])
  .then((results) => (filtering.value = results));
</script>
