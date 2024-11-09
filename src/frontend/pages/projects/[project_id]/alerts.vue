<template>
  <MenuProject>
    <Dataset
      ref="dataset"
      :api="api"
      :add="AlertDialog"
      :filtering="filtering"
      :default-parameters="{ project: route.params.project_id }"
      icon="mdi-alert"
      empty-head="No Alerts"
      empty-text="There are no alerts yet. Create your first one"
      cols="4"
    >
      <template #item="{ item }">
        <AlertShow
          v-if="!item.value"
          :api="api"
          :alert="item"
          @reload="dataset.loadData(false)"
        />
        <v-dialog v-if="item.value !== null">
          <template #activator="{ props: activatorProps }">
            <AlertShow
              :api="api"
              :alert="item"
              hover
              v-bind="activatorProps"
              @reload="dataset.loadData(false)"
            />
          </template>
          <template #default="{ isActive }">
            <AlertDialog
              :api="api"
              :edit="item"
              @completed="
                dataset.loadData(false);
                isActive.value = false;
              "
              @close-dialog="isActive.value = false"
            />
          </template>
        </v-dialog>
      </template>
    </Dataset>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const AlertDialog = resolveComponent("AlertDialog");
const dataset = ref(null);
const user = userStore();
const route = useRoute();
const enums = ref(useEnums());
const filters = useFilters();
const api = useApi("/api/alerts/", true, "Alert");
const filtering = ref([]);
filters
  .build([
    {
      type: "autocomplete",
      label: "Mode",
      collection: filters.collectionFromEnum(enums.value.alertModes),
      cols: 2,
      fieldValue: "name",
      fieldTitle: "name",
      key: "mode",
    },
    {
      type: "autocomplete",
      label: "Item",
      collection: filters.collectionFromEnum(enums.value.alertItems),
      fieldValue: "name",
      fieldTitle: "name",
      key: "item",
    },
    {
      type: "switch",
      label: "Enabled",
      color: "green",
      cols: 1,
      key: "enabled",
      trueValue: true,
      falseValue: null,
    },
    {
      type: "switch",
      label: "Subscribed",
      color: "red",
      cols: 2,
      key: "subscribers",
      trueValue: user.user,
      falseValue: null,
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
      type: "autocomplete",
      label: "Sort",
      icon: "mdi-sort",
      cols: 2,
      collection: ["id", "item", "mode"],
      fieldValue: "id",
      fieldTitle: "name",
      key: "ordering",
      defaultValue: "id",
    },
  ])
  .then((results) => (filtering.value = results));
</script>
