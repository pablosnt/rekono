<template>
  <v-container fluid>
    <v-row v-if="header" justify="center" dense>
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
          !expandFilters ? resetParameters() : null;
          $emit('expandFilters', expandFilters);
        "
      />
      <slot name="add">
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
            <!-- todo: Check when add must be displayed depending on the user roles -->
            <component
              :is="add"
              :api="api"
              :parameters="defaultParameters"
              @completed="
                loadData(true);
                isActive.value = false;
              "
              @close-dialog="isActive.value = false"
            />
          </template>
        </v-dialog>
      </slot>
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
                hide-details
                clearable
                :chips="f.multiple ? f.multiple : undefined"
                density="comfortable"
                variant="outlined"
                :label="f.label"
                :items="f.collection"
                :item-title="f.fieldTitle"
                return-object
                :color="
                  f.multiple
                    ? f.value.length > 0 && f.value[0].color
                      ? f.value[0].color
                      : null
                    : f.value && f.value.color
                      ? f.value.color
                      : null
                "
                :prepend-inner-icon="
                  f.enforceIcon
                    ? f.icon
                    : f.multiple
                      ? f.value.length > 0 && f.value[0].icon
                        ? f.value[0].icon
                        : f.icon
                      : f.value && f.value.icon
                        ? f.value.icon
                        : f.icon
                "
                :disabled="f.disabled ? f.disabled : false"
                :multiple="f.multiple ? f.multiple : false"
                @update:model-value="addParameter(f.key, filters.getValue(f))"
              >
                <!-- todo: Override list items to show custom icons per option -->
                <template
                  v-if="f.key.includes('task')"
                  #item="{ props: taskProps, item }"
                >
                  <v-list-item
                    v-bind="taskProps"
                    :title="tasks.getTitle(item.raw)"
                  />
                </template>
                <template v-if="f.key.includes('task')" #selection="{ item }">
                  <p>{{ tasks.getTitle(item.raw) }}</p>
                </template>
              </v-autocomplete>
              <v-text-field
                v-if="f.type === 'text'"
                v-model="f.value"
                hide-details
                clearable
                density="comfortable"
                variant="outlined"
                :label="f.label"
                :prepend-inner-icon="f.icon"
                :disabled="f.disabled ? f.disabled : false"
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
                :disabled="f.disabled ? f.disabled : false"
                @update:model-value="addParameter(f.key, f.value)"
              />
            </v-col>
          </template>
        </v-row>
      </v-container>
    </v-expand-transition>
  </v-container>
  <v-container fluid>
    <v-progress-linear
      v-if="loadingData"
      height="5"
      color="red"
      indeterminate
      rounded
    />
    <v-row
      v-if="
        data !== null &&
        icon !== null &&
        (emptyHead !== undefined ||
          emptyTitle !== undefined ||
          emptyText !== undefined) &&
        data.length === 0
      "
      justify="center"
      dense
    >
      <v-empty-state
        :icon="icon"
        :headline="emptyHead"
        :title="emptyTitle"
        :text="emptyText"
      >
        <template #media>
          <v-icon class="mb-3" color="red-darken-4" />
        </template>
      </v-empty-state>
    </v-row>
    <slot v-if="data !== null && data.length > 0" name="data" />
  </v-container>

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
  filtering: {
    type: Array<object>,
    required: false,
    default: [],
  },
  expandFilters: {
    type: Boolean,
    required: false,
    default: false,
  },
  header: {
    type: Boolean,
    required: false,
    default: true,
  },
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
  icon: {
    type: String,
    required: false,
    default: null,
  },
  emptyHead: {
    type: String,
    required: false,
    default: undefined,
  },
  emptyTitle: {
    type: String,
    required: false,
    default: undefined,
  },
  emptyText: {
    type: String,
    required: false,
    default: undefined,
  },
});
const emit = defineEmits(["loadData", "expandFilters"]);
const tasks = useTasks();
const filters = useFilters();
const page = ref(1);
const total = ref(0);
const data = ref(null);
const search = ref(null);
const parameters = ref(loadParameters());
const loadingSearch = ref(false);
const loadingData = ref(false);
const expandFilters = ref(props.expandFilters);
let changedFilters = false;
loadData(true);

function loadParameters() {
  const parameters =
    props.defaultParameters === null
      ? {}
      : Object.assign({}, props.defaultParameters);
  if (props.filtering) {
    for (let i = 0; i < props.filtering.length; i++) {
      const value = filters.getValue(props.filtering[i]);
      if (value !== null && value !== undefined) {
        parameters[props.filtering[i].key] = value;
      }
    }
  }
  // TODO: Load parameters from URL query parameters
  return parameters;
}

function resetParameters() {
  if (changedFilters) {
    props.filtering.map((item) => {
      filters.setDefault(item);
      if (item.callback) {
        item.callback(item.value, props.filtering);
      }
    });
    // TODO: Without those from URL query params
    parameters.value = loadParameters();
    changedFilters = false;
    loadData(true);
  }
}

function addParameter(key: string, value: string) {
  changedFilters = true;
  const definition = filters.getDefinitionFromKey(key, props.filtering);
  if (definition.callback) {
    definition.callback(value, props.filtering);
    loadParameters();
  } else {
    // TODO: Keep parameters as URL parameter to allow links with filters from other pages or provided by users. Needed to link findings between them
    if (value !== null) {
      parameters.value[key] = value;
    } else {
      /* eslint-disable-next-line @typescript-eslint/no-dynamic-delete */
      delete parameters.value[key];
    }
  }
  loadData();
}

function loadData(loading: boolean = false) {
  if (parameters.value) {
    if (search.value) {
      loadingSearch.value = true;
      parameters.value.search = search.value;
    } else if (parameters.value.search) {
      delete parameters.value.search;
    }
  }
  if (loading) {
    loadingData.value = true;
  }
  props.api.list(parameters.value, false, page.value).then((response) => {
    emit("loadData", response.items);
    total.value = response.total;
    data.value = response.items;
    loadingSearch.value = false;
    loadingData.value = false;
  });
}

// todo: Define parameters typing properly in all functions

defineExpose({ loadData });
</script>
