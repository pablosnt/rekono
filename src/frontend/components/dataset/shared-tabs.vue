<template>
  <v-tabs
    v-model="tab"
    align-tabs="center"
    fixed-tabs
    @update:model-value="tabChange()"
  >
    <v-tab
      v-for="t in tabKeys"
      :key="t"
      :value="t"
      :text="tabs[t].text"
      :prepend-icon="tabs[t].icon"
      color="red-darken-2"
    />
  </v-tabs>
  <Dataset
    v-if="filtering.length > 0"
    ref="dataset"
    :key="forceUpdate"
    :api="tabs[tab].api"
    :icon="tabs[tab].icon"
    :filtering="filtering"
    :expand-filters="expandFilters"
    :default-parameters="defaultParameters"
    :empty-head="tabs[tab].emptyHead"
    :empty-text="tabs[tab].emptyText"
    @load-data="(data) => (collection = data)"
    @expand-filters="(value) => (expandFilters = value)"
  >
    <template #data>
      <v-tabs-window v-model="tab">
        <v-container fluid>
          <v-row dense>
            <v-col
              v-for="item in collection"
              :key="item.id"
              :cols="tabs[tab].cols ? tabs[tab].cols : '6'"
            >
              <v-tabs-window-item v-for="t in tabKeys" :key="t" :value="t">
                <component
                  :is="tabs[tab].component"
                  v-bind="properties(item)"
                  @reload="dataset.loadData(false)"
                />
              </v-tabs-window-item>
            </v-col>
          </v-row>
        </v-container>
      </v-tabs-window>
    </template>
  </Dataset>
</template>

<script setup lang="ts">
const props = defineProps({
  tabs: Object,
  defaultParameters: Object,
  defaultProperties: { type: Object, required: false, default: null },
  globalFiltering: { type: Array, required: false, default: null },
  conditionalFiltering: { type: Array, required: false, default: null },
  conditionalField: { type: String, required: false, default: null },

  entity: String,
  matchQuery: { type: Boolean, required: false, default: false },
});
const route = useRoute();
const router = useRouter();
const filters = useFilters();

const forceUpdate = ref(0);
const expandFilters = ref(false);
const dataset = ref(null);
const collection = ref([]);
const tabKeys = ref(Object.keys(props.tabs));
const tabQuery = route.query.tab?.toString().toLowerCase();
const tab = ref(tabKeys.value.includes(tabQuery) ? tabQuery : tabKeys.value[0]);
const filtering = ref([]);
buildFiltering();

function properties(item) {
  return Object.assign(
    {},
    {
      api: props.tabs[tab.value].api,
      [props.entity]: item,
    },
    props.defaultProperties !== null ? props.defaultProperties : {},
  );
}

function buildFiltering() {
  filters.build(props.tabs[tab.value].filtering).then((tabFilters) => {
    filters
      .build(
        props.globalFiltering !== null && props.globalFiltering.length > 0
          ? props.globalFiltering
          : [],
      )
      .then((globalFilters) => {
        filters
          .build(
            props.conditionalFiltering !== null &&
              props.conditionalFiltering.length > 0 &&
              props.conditionalField !== null &&
              props.tabs[tab.value][props.conditionalField]
              ? props.globalFiltering
              : [],
          )
          .then((conditionalFilters) => {
            filters
              .build([
                {
                  type: "autocomplete",
                  label: "Sort",
                  icon: "mdi-sort",
                  cols: 2,
                  collection: props.tabs[tab.value].ordering,
                  fieldValue: "id",
                  fieldTitle: "name",
                  key: "ordering",
                  defaultValue: "-id",
                },
              ])
              .then((orderFilters) => {
                filtering.value = tabFilters
                  .concat(globalFilters)
                  .concat(conditionalFilters)
                  .concat(orderFilters);
              });
          });
      });
  });
}

function tabChange() {
  buildFiltering();
  forceUpdate.value++;
  if (dataset.value) {
    collection.value = [];
    dataset.value.loadData(true);
  }
  if (props.matchQuery) {
    router.replace({
      query: Object.assign({}, route.query, { tab: tab.value }),
    });
  }
}
</script>
