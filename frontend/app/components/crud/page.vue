<template>
  <div v-if="mounted">
    <template v-if="config.canRead">
      <CrudHeader
        :api="api"
        :open-create-modal="openCreateModal"
        :config="config"
        :state="state"
        :table="tableRef"
        :filters-open="Object.keys(initialFiltersFromUrl).length > 0"
        :disable-url-sync="disableUrlSync"
        @search="
          (search: string) => {
            state.loading = true;
            state.searchQuery = search;
            fetchFirstPage();
          }
        "
        @filters="
          (filters: Record<string, any>) => {
            state.loading = true;
            state.filters = filters;
            if (
              Object.keys(filters).length ===
                Object.keys(config.defaultFilters || {}).length &&
              !disableUrlSync
            )
              router.replace({ query: {} });
            fetchFirstPage();
          }
        "
        @ordering="
          (sorting: string) => {
            state.ordering = sorting;
            fetchFirstPage();
          }
        "
        @create="fetch()"
        @open-create="(open: boolean) => (openCreateModal = open)"
      >
        <template v-if="$slots['header-leading']" #header-leading>
          <slot name="header-leading" />
        </template>
        <template v-if="$slots['header-actions']" #header-actions>
          <slot name="header-actions" />
        </template>
        <template v-if="$slots['create-button']" #create-button>
          <slot name="create-button" />
        </template>
      </CrudHeader>

      <slot name="before" :state="state" />

      <slot name="content">
        <UProgress
          :class="[
            state.loading && state.items.length === 0 ? 'visible' : 'invisible',
            'mb-1',
          ]"
        />
        <template v-if="config.tableColumns">
          <CrudTable
            v-if="state.items.length > 0"
            ref="tableRef"
            :config="config"
            :state="state"
            @edit="
              (item) => {
                selectedItem = item;
                openEditModal = true;
              }
            "
            @delete="
              (item) => {
                selectedItem = item;
                openDeleteModal = true;
              }
            "
          >
            <template v-if="$slots.actions" #actions="slotProps">
              <slot name="actions" v-bind="slotProps" />
            </template>
          </CrudTable>
          <CrudEmptyState
            v-else-if="!state.loading"
            :config="config"
            :state="state"
            class="py-12"
            @create-click="onCreateClick"
          />
        </template>

        <template v-else-if="config.useGrid">
          <CrudEmptyState
            v-if="state.items.length === 0 && !state.loading"
            :config="config"
            :state="state"
            class="mt-10"
            @create-click="onCreateClick"
          />
          <UPageGrid v-show="state.items.length > 0">
            <slot
              v-for="item in state.items"
              :key="item.id"
              name="item"
              :item="item"
              :on-edit="
                () => {
                  selectedItem = item;
                  openEditModal = true;
                }
              "
              :on-delete="
                () => {
                  selectedItem = item;
                  openDeleteModal = true;
                }
              "
            />
          </UPageGrid>
        </template>

        <LazyCrudFormModal
          v-if="config.canEdit"
          :open="openEditModal"
          :api="api"
          :config="config"
          :item="selectedItem"
          @open="
            (open: boolean) => {
              openEditModal = open;
              if (!open && config.updateOnEditModalOpen) {
                fetch();
              }
            }
          "
          @submit="fetch()"
        />

        <LazyCrudDeleteModal
          v-if="config.canDelete"
          :open="openDeleteModal"
          :api="api"
          :config="config"
          :item="selectedItem"
          @open="(open: boolean) => (openDeleteModal = open)"
          @deleted="
            () => {
              fetch();
              $emit('deleted');
            }
          "
        />

        <CrudPagination
          :config="config"
          :state="state"
          @page="
            (page: number) => {
              state.page = page;
              if (!disableUrlSync)
                router.replace({
                  query: { ...route.query, page: String(page) },
                });
              fetch();
            }
          "
          @page-size="
            (size: number) => {
              state.pageSize = size;
              state.page = 1;
              if (!disableUrlSync)
                router.replace({
                  query: { ...route.query, limit: String(size) },
                });
              fetch();
            }
          "
        />
      </slot>
    </template>

    <template v-else>
      <UError
        v-if="[true, undefined].includes(config.showAccessDeniedError)"
        :error="{
          statusCode: 403,
          statusMessage: 'Access Denied',
          message:
            'You do not have the necessary permissions to view this page',
        }"
        redirect="/"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState } from "~/types/crud";

const props = defineProps<{ config: CrudConfig; disableUrlSync?: boolean }>();
const emit = defineEmits<{
  fetched: [items: unknown[]];
  deleted: [];
  createClick: [];
}>();

const api = useApi(props.config.endpoint);
const route = useRoute();
const router = useRouter();
const tableRef = ref();
const openCreateModal = ref(false);
const openEditModal = ref(false);
const openDeleteModal = ref(false);
const selectedItem = ref(null);
const mounted = ref(false);
const urlFilterKeys = computed(() => {
  const keys = new Set<string>();
  for (const f of props.config.filters ?? []) {
    if (f.type === "range" && f.multiple) {
      keys.add(`${f.key}__gte`);
      keys.add(`${f.key}__lte`);
    } else {
      keys.add(f.key);
    }
  }
  return keys;
});
const initialFiltersFromUrl = props.disableUrlSync
  ? {}
  : Object.fromEntries(
      Object.entries(route.query)
        .filter(
          ([key, value]) =>
            ![undefined, null, "false"].includes(value) &&
            typeof value === "string" &&
            urlFilterKeys.value.has(key) &&
            (!props.config.defaultFilters ||
              !Object.keys(props.config.defaultFilters).includes(key)),
        )
        .map(([key, value]) => {
          const num = Number(value as string);
          return [
            key,
            value === "true" ? true : value !== "" && !isNaN(num) ? num : value,
          ];
        }),
    );

const defaultPageSize = props.config.pageSize || 24;
const state = reactive<CrudState>({
  items: [],
  total: 0,
  loading: true,
  page:
    !props.disableUrlSync && route.query.page
      ? parseInt(route.query.page as string) || 1
      : 1,
  pageSize:
    !props.disableUrlSync && route.query.limit
      ? parseInt(route.query.limit) || defaultPageSize
      : defaultPageSize,
  filters: {
    ...(props.config.defaultFilters
      ? JSON.parse(JSON.stringify(props.config.defaultFilters))
      : {}),
    ...initialFiltersFromUrl,
  },
  searchQuery:
    props.config.searchable && !props.disableUrlSync && route.query.search
      ? route.query.search
      : undefined,
  ordering: props.config.defaultOrdering,
});

function fetch() {
  state.loading = true;
  let params = state.filters;
  if (props.config.searchable && state.searchQuery) {
    params = { ...params, search: state.searchQuery };
  }
  if (state.ordering) {
    params = { ...params, ordering: state.ordering };
  }
  api
    .list("", params, false, state.page, state.pageSize)
    .then((response: object) => {
      state.items = response.items;
      state.total = response.total;
      emit("fetched", response.items);
    })
    .finally(() => {
      state.loading = false;
    });
}

function fetchFirstPage() {
  state.page = 1;
  fetch();
}

function onCreateClick() {
  openCreateModal.value = true;
  emit("createClick");
}

onMounted(() => {
  mounted.value = true;
  if (props.config.canRead && props.config.endpoint) {
    fetch();
  }
});

defineExpose({ fetch });
</script>
