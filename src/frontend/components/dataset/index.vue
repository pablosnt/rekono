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
        @update:model-value="addParameter('search', search)"
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
            <!-- TODO: Check when add must be displayed depending on the user roles -->
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
                  f.value !== null && f.value !== undefined
                    ? f.multiple
                      ? f.value.length > 0 && f.value[0].color
                        ? f.value[0].color
                        : null
                      : f.value && f.value.color
                        ? f.value.color
                        : null
                    : null
                "
                :prepend-inner-icon="
                  f.enforceIcon || f.value === null || f.value === undefined
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
                <!-- TODO: Override list items to show custom icons per option -->
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
    <slot v-if="data !== null && data.length > 0" name="data">
      <slot name="prepend-data" />
      <v-row dense>
        <v-col
          v-for="item in data"
          :key="item.id ? item.id : item"
          :cols="cols"
        >
          <slot name="item" :item="item" />
        </v-col>
      </v-row>
    </slot>
  </v-container>

  <v-pagination
    v-model="page"
    :length="Math.ceil(total / api.default_size)"
    rounded="circle"
    @update:model-value="loadData"
  />
  <!-- TODO: keep page in query params -->
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
  cols: {
    type: String,
    required: false,
    default: "6",
  },
});
const emit = defineEmits(["loadData", "expandFilters"]);
const tasks = useTasks();
const filters = useFilters();
const route = useRoute();
const router = useRouter();
const page = ref(1);
const total = ref(0);
const data = ref(null);
const search = ref(null);
const expandFilters = ref(props.expandFilters);
const parameters = ref(loadParameters());
const loadingSearch = ref(false);
const loadingData = ref(false);
let changedFilters = false;
loadData(true);

function loadParameters(): object {
  const parameters =
    props.defaultParameters === null
      ? {}
      : Object.assign({}, props.defaultParameters);
  if (props.filtering) {
    for (const definition of props.filtering) {
      const value = filters.getValue(definition);
      if (value !== null && value !== undefined) {
        parameters[definition.key] = value;
        if (definition.callback) {
          definition.callback(value, props.filtering);
        }
      }
    }
    expandFilters.value =
      Object.keys(route.query).filter((k) => k !== "tab").length > 0;
  }
  return parameters;
}

function resetParameters(): void {
  if (changedFilters) {
    props.filtering.map((item) => {
      filters.setDefault(item);
      if (item.callback) {
        item.callback(item.value, props.filtering);
      }
    });
    router.replace({ query: {} });
    parameters.value = loadParameters();
    changedFilters = false;
    loadData(true);
  }
}

function addParameter(key: string, value: string): void {
  changedFilters = true;
  const queryParams = Object.assign({}, route.query);
  if (value !== null && value !== undefined) {
    parameters.value[key] = value;
    queryParams[key] = value;
  } else {
    /* eslint-disable-next-line @typescript-eslint/no-dynamic-delete */
    delete parameters.value[key];
    /* eslint-disable-next-line @typescript-eslint/no-dynamic-delete */
    delete queryParams[key];
    value = null;
  }
  router.replace({ query: queryParams });
  const definition = filters.getDefinitionFromKey(key, props.filtering);
  if (definition && definition.callback) {
    definition.callback(value, props.filtering);
    parameters.value = Object.assign({}, loadParameters(), parameters.value);
  }
  loadData();
}

function loadData(loading: boolean = false): void {
  if (search.value) {
    loadingSearch.value = true;
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

// CODE: Define parameters typing properly in all JS functions

defineExpose({ loadData });
</script>
