<template>
  <v-container fluid>
    <v-row justify="center" dense>
      <v-text-field
        v-model="search"
        :loading="loadingSearch"
        prepend-inner-icon="mdi-magnify"
        label="Search"
        variant="outlined"
        hide-details
        single-line
        autofocus
        clearable
        @update:model-value="loadData"
      />
      <v-btn
        v-if="filtering?.length > 0"
        :icon="
          expandFilters ? 'mdi-flip-v mdi-filter-variant' : 'mdi-filter-variant'
        "
        variant="text"
        size="large"
        @click="
          expandFilters = !expandFilters;
          !expandFilters ? collapseFilters() : null;
        "
      />
      <v-dialog
        v-if="add !== null"
        :width="addFullscreen ? '100%' : 'auto'"
        :fullscreen="addFullscreen"
      >
        <template #activator="{ props: activatorProps }">
          <v-btn
            icon="mdi-plus-thick"
            variant="text"
            size="large"
            color="green"
            v-bind="activatorProps"
          />
        </template>
        <template #default="{ isActive }">
          <component
            :is="add"
            :api="api"
            @completed="loadData(true)"
            @close-dialog="isActive.value = false"
          />
        </template>
      </v-dialog>
    </v-row>
    <v-expand-transition>
      <v-container v-if="expandFilters" fluid class="mb-0">
        <v-row justify="center" dense>
          <template v-for="f in filtering" :key="f.key">
            <v-col
              class="d-flex justify-center align-center"
              :cols="f.cols ? f.cols : 3"
            >
              <v-autocomplete
                v-if="f.type === 'autocomplete'"
                v-model="f.value"
                auto-select-first
                clearable
                hide-details
                density="comfortable"
                variant="outlined"
                :label="f.label"
                :items="
                  f.key !== 'ordering'
                    ? f.collection
                    : getSortItems(f.collection)
                "
                :item-title="f.fieldTitle"
                return-object
                :color="f.value && f.value.color ? f.value.color : null"
                :prepend-inner-icon="f.icon"
                @update:model-value="
                  addParameter(
                    f.key,
                    f.value && f.fieldValue ? f.value[f.fieldValue] : f.value,
                  )
                "
              />
              <v-text-field
                v-if="f.type === 'text'"
                v-model="f.value"
                hide-details
                clearable
                density="comfortable"
                variant="outlined"
                :label="f.label"
                :prepend-inner-icon="f.icon"
                @update:model-value="addParameter(f.key, f.value)"
              />
              <v-switch
                v-if="f.type === 'switch'"
                v-model="f.value"
                hide-details
                :label="f.label"
                :color="f.color"
                :true-value="f.trueValue"
                :false-value="f.falseValue"
                @update:model-value="addParameter(f.key, f.value)"
              />
            </v-col>
          </template>
        </v-row>
      </v-container>
    </v-expand-transition>
  </v-container>
  <v-container v-if="loadingData" fluid>
    <v-progress-linear height="5" color="red" indeterminate rounded />
  </v-container>
  <slot name="data" />
  <v-pagination
    v-model="page"
    :length="Math.ceil(total / api.default_size)"
    rounded="circle"
    @update:model-value="loadData"
  />
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  filtering: Array<object>,
  ordering: String,
  add: {
    type: Object,
    required: false,
    default: null,
  },
  addFullscreen: {
    type: Boolean,
    required: false,
    default: false,
  },
  defaultParameters: {
    type: Object,
    required: false,
    default: null,
  },
});
const emit = defineEmits(["loadData"]);
const page = ref(1);
const total = ref(0);
const search = ref(null);
const parameters = ref(
  props.defaultParameters && props.ordering
    ? Object.assign({}, props.defaultParameters, { ordering: props.ordering })
    : props.defaultParameters
      ? props.defaultParameters
      : props.ordering
        ? { ordering: props.ordering }
        : {},
);
const loadingSearch = ref(false);
const loadingData = ref(false);
const expandFilters = ref(false);
function collapseFilters() {
  if (
    Object.keys(parameters.value).length !== 1 ||
    parameters.value.ordering !== props.ordering
  ) {
    parameters.value = props.ordering ? { ordering: props.ordering } : {};
    loadData(true);
    Object.entries(props.filtering).map(([_, v]) => {
      v.value = null;
    });
  }
}
function addParameter(key: string, value: string) {
  if (value !== null && value !== undefined) {
    parameters.value[key] = value;
  } else if (key === "ordering" && props.ordering) {
    parameters.value.ordering = props.ordering;
  } else {
    /* eslint-disable @typescript-eslint/no-dynamic-delete */
    delete parameters.value[key];
    /* eslint-enable @typescript-eslint/no-dynamic-delete */
  }
  loadData();
}
function loadData(loading: boolean = false) {
  if (search.value) {
    loadingSearch.value = true;
    parameters.value.search = search.value;
  } else if (parameters.value.search) {
    delete parameters.value.search;
  }
  if (loading) {
    loadingData.value = true;
  }
  props.api.list(parameters.value, false, page.value).then((response) => {
    emit("loadData", response.items);
    total.value = response.total;
    loadingSearch.value = false;
    loadingData.value = false;
  });
}
loadData(true);
function getSortItems(collection: Array<string>) {
  return collection
    .map((item) => {
      let name =
        item === "id"
          ? "ID"
          : `${item.charAt(0).toUpperCase()}${item.slice(1)}`;
      name = name.includes("_") ? name.split("_")[0] : name;
      return [
        { id: item, name: name },
        { id: `-${item}`, name: `${name} desc` },
      ];
    })
    .flat(1);
}
defineExpose({ loadData });
</script>
