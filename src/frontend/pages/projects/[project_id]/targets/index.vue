<template>
  <MenuProject>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :default-parameters="{ project: route.params.project_id }"
      :add="TargetDialog"
      auditor
      icon="mdi-target"
      empty-head="No Targets"
      :empty-text="
        user.role === 'Reader'
          ? 'There are no targets yet'
          : 'Create your first target to start hacking'
      "
      cols="4"
    >
      <template #item="{ item }">
        <v-card
          :title="item.target"
          :subtitle="item.type"
          elevation="2"
          class="ma-3"
          density="comfortable"
          :prepend-icon="enums.targets[item.type].icon"
          :to="`/projects/${item.project}/targets/${item.id}/dashboard`"
          hover
        >
          <template #append>
            <BaseButton
              icon="mdi-card-multiple mdi-rotate-90"
              variant="plain"
              tooltip="Copy target"
              @click.prevent.stop="copy(item)"
            />
          </template>
          <v-card-actions>
            <TaskButton v-if="project" :project="project" :target="item" />
            <v-spacer />
            <TargetButtonLinks
              :target="item"
              :integration="integration"
              :settings="settings"
            />
            <TargetButtonActions
              :target="item"
              :api="api"
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
const alert = useAlert();
const project = ref(null);
useApi("/api/projects/", true)
  .get(parseInt(route.params.project_id))
  .then((response) => (project.value = response));
const TargetDialog = resolveComponent("TargetDialog");
const dataset = ref(null);
const api = useApi("/api/targets/", true, "Target");
const integration = ref({ enabled: false });
const settings = ref({ is_available: false });
useApi("/api/integrations/", true)
  .get(1)
  .then((integrationResponse) => {
    integration.value = integrationResponse;
  });
useApi("/api/defect-dojo/settings/", true)
  .get(1)
  .then((settingsResponse) => {
    settings.value = settingsResponse;
  });
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

function copy(target: object): void {
  navigator.clipboard.writeText(target.target);
  alert("Target copied to the clipboard", "success");
}
</script>
