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
      @load-data="(data) => (targets = data)"
    >
      <template #data>
        <v-row dense>
          <v-col v-for="target in targets" :key="target.id" cols="6">
            <v-card
              :title="target.target"
              :subtitle="target.type"
              elevation="2"
              class="mx-auto"
              density="compact"
              :prepend-icon="enums.targets[target.type].icon"
              :to="`/projects/${target.project}/targets/${target.id}/dashboard`"
            >
              <template #append>
                <UtilsCounter
                  :collection="target.tasks"
                  tooltip="Tasks"
                  icon="mdi-play-network"
                  :link="`/projects/${target.project}/scans`"
                  color="red"
                  new-tab
                />
                <UtilsCounter
                  class="ml-2"
                  :collection="target.reports"
                  tooltip="Reports"
                  icon="mdi-file-document-multiple"
                  :link="`/projects/${target.project}/reports`"
                  color="blue-grey-darken-1"
                  new-tab
                />
                <UtilsCounter
                  class="ml-2"
                  :collection="target.notes"
                  tooltip="Notes"
                  icon="mdi-notebook"
                  :link="`/projects/${target.project}/notes`"
                  color="indigo-darken-1"
                  new-tab
                />
                <!-- CODE: Link (Defect-Dojo) -->
              </template>
              <v-card-actions>
                <TaskButton
                  v-if="project"
                  :project="project"
                  :target="target"
                />
                <v-spacer />
                <NoteButton
                  :project="route.params.project_id"
                  :target="target"
                />
                <ReportButton
                  :project="route.params.project_id"
                  :target="target"
                />
                <UtilsButtonDelete
                  :id="target.id"
                  :api="api"
                  :text="`Target '${target.target}' will be removed`"
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
const targets = ref([]);
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
