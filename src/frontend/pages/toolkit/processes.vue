<template>
  <MenuToolkit>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :add="ProcessDialog"
      add-fullscreen
      icon="mdi-robot-angry"
      empty-head="No Processes"
      empty-text="There are no processes. Create your first one"
      @load-data="(data) => (processes = data)"
    >
      <template #data>
        <v-row dense>
          <v-col v-for="process in processes" :key="process.id" cols="4">
            <v-dialog width="100%" fullscreen>
              <template #activator="{ props: activatorProps }">
                <ProcessShow
                  :api="api"
                  :process="process"
                  :tools="tools"
                  :details="false"
                  v-bind="activatorProps"
                  @reload="(value) => dataset.loadData(value)"
                />
              </template>
              <template #default="{ isActive }">
                <ProcessShow
                  :api="api"
                  :process="process"
                  :tools="tools"
                  details
                  @reload="(value) => dataset.loadData(value)"
                  @close-dialog="isActive.value = false"
                />
              </template>
            </v-dialog>
          </v-col>
        </v-row>
      </template>
    </Dataset>
  </MenuToolkit>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const user = userStore();
const enums = useEnums();
const filters = useFilters();
const ProcessDialog = resolveComponent("ProcessDialog");
const dataset = ref(null);
const processes = ref(null);
const api = ref(useApi("/api/processes/", true, "Process"));
const tools = ref([]);
const filtering = ref(
  filters.build([
    {
      type: "autocomplete",
      label: "Stage",
      icon: "mdi-stairs",
      cols: 2,
      collection: filters.collectionFromEnum(enums.stages),
      fieldValue: "id",
      fieldTitle: "name",
      key: "stage",
    },
    {
      type: "text",
      label: "Tag",
      icon: "mdi-tag",
      cols: 2,
      key: "tag",
    },
    {
      type: "switch",
      label: "Mine",
      color: "blue",
      cols: 1,
      key: "owner",
      trueValue: user.user,
      falseValue: null,
    },
    {
      type: "switch",
      label: "Likes",
      color: "red",
      cols: 1,
      key: "like",
      trueValue: true,
      falseValue: null,
    },
    {
      type: "autocomplete",
      label: "Sort",
      icon: "mdi-sort",
      cols: 2,
      collection: ["id", "name", "likes_count"],
      fieldValue: "id",
      fieldTitle: "name",
      key: "ordering",
      defaultValue: "id",
    },
  ]),
);
useApi("/api/tools/", true, "Tool")
  .list({}, true)
  .then((response) => {
    tools.value = response.items;
    filtering.value = filters
      .process([
        {
          type: "autocomplete",
          label: "Tool",
          icon: "mdi-rocket",
          cols: 2,
          collection: tools.value,
          fieldValue: "id",
          fieldTitle: "name",
          key: "tool",
          enforceIcon: true,
        },
      ])
      .concat(filtering.value);
  });
</script>
