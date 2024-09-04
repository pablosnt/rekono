<template>
  <MenuToolkit>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      ordering="id"
      :add="ProcessDialog"
      :add-fullscreen="true"
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
                  :details="true"
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
const ProcessDialog = resolveComponent("ProcessDialog");
const dataset = ref(null);
const processes = ref(null);
const api = ref(useApi("/api/processes/", true, "Process"));
const tools = ref([]);
const filtering = ref([
  {
    type: "autocomplete",
    label: "Stage",
    icon: "mdi-stairs",
    cols: 2,
    collection: Object.entries(enums.stages).map(([k, v]) => {
      v.name = k;
      return v;
    }),
    fieldValue: "id",
    fieldTitle: "name",
    key: "stage",
    value: null,
  },
  {
    type: "text",
    label: "Tag",
    icon: "mdi-tag",
    cols: 2,
    key: "tag",
    value: null,
  },
  {
    type: "switch",
    label: "Mine",
    color: "blue",
    cols: 1,
    key: "owner",
    trueValue: user.user,
    falseValue: null,
    value: null,
  },
  {
    type: "switch",
    label: "Likes",
    color: "red",
    cols: 1,
    key: "like",
    trueValue: true,
    falseValue: null,
    value: null,
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
    value: "id",
  },
]);
useApi("/api/tools/", true, "Tool")
  .list({}, true)
  .then((response) => {
    tools.value = response.items;
    filtering.value = [
      {
        type: "autocomplete",
        label: "Tool",
        icon: "mdi-rocket",
        cols: 2,
        collection: tools.value,
        fieldValue: "id",
        fieldTitle: "name",
        key: "tool",
        value: null,
      },
    ].concat(filtering.value);
  });
</script>
