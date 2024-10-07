<template>
  <MenuProject>
    <Dataset
      ref="dataset"
      :api="api"
      :add="AlertDialog"
      :filtering="filtering"
      :default-parameters="{ project: route.params.project_id }"
      ordering="id"
      icon="mdi-alert"
      empty-head="No Alerts"
      empty-text="There are no alerts yet. Create your first one"
      @load-data="(data) => (alerts = data)"
    >
      <template #data>
        <v-row dense>
          <v-col v-for="alert in alerts" :key="alert.id" cols="4">
            <AlertShow
              v-if="!alert.value"
              :api="api"
              :alert="alert"
              @reload="dataset.loadData(false)"
            />
            <v-dialog v-if="alert.value !== null">
              <template #activator="{ props: activatorProps }">
                <AlertShow
                  :api="api"
                  :alert="alert"
                  hover
                  v-bind="activatorProps"
                  @reload="dataset.loadData(false)"
                />
              </template>
              <template #default="{ isActive }">
                <AlertDialog
                  :api="api"
                  :edit="alert"
                  @completed="
                    dataset.loadData(false);
                    isActive.value = false;
                  "
                  @close-dialog="isActive.value = false"
                />
              </template>
            </v-dialog>
          </v-col>
        </v-row>
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
const api = useApi("/api/alerts/", true, "Alert");
const alerts = ref([]);
const filtering = ref([
  {
    type: "autocomplete",
    label: "Mode",
    collection: Object.entries(enums.value.alertModes).map(([k, v]) => {
      v.name = k;
      return v;
    }),
    cols: 2,
    fieldValue: "name",
    fieldTitle: "name",
    key: "mode",
    value: null,
  },
  {
    type: "autocomplete",
    label: "Item",
    collection: Object.entries(enums.value.alertItems).map(([k, v]) => {
      v.name = k;
      return v;
    }),
    fieldValue: "name",
    fieldTitle: "name",
    key: "item",
    value: null,
  },
  {
    type: "switch",
    label: "Enabled",
    color: "green",
    cols: 1,
    key: "enabled",
    trueValue: true,
    falseValue: null,
    value: null,
  },
  {
    type: "switch",
    label: "Subscribed",
    color: "red",
    cols: 2,
    key: "subscribers",
    trueValue: user.user,
    falseValue: null,
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
    type: "autocomplete",
    label: "Sort",
    icon: "mdi-sort",
    cols: 2,
    collection: ["id", "item", "mode"],
    fieldValue: "id",
    fieldTitle: "name",
    key: "ordering",
    value: "id",
  },
]);
</script>
