<template>
  <div v-if="mounted">
    <template v-if="config.canRead">
      <CrudHeader
        :api="api"
        :open-create-modal="openCreateModal"
        :config="config"
        :state="state"
        :table="tableRef"
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
      </CrudHeader>

      <slot name="before" :state="state" />

      <slot name="content">
        <CrudEmptyState
          v-if="state.items.length === 0 && !state.loading && config.useGrid"
          :config="config"
          :state="state"
          class="mt-10"
          @create-click="openCreateModal = true"
        />

        <CrudTable
          v-if="config.tableColumns && !config.useGrid"
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
          <template #empty>
            <CrudEmptyState
              v-if="!state.loading"
              :config="config"
              :state="state"
              container-class="py-12"
              @create-click="openCreateModal = true"
            />
            <UButton v-else size="xl" loading variant="ghost" />
          </template>
        </CrudTable>

        <template v-if="config.useGrid">
          <UProgress
            :class="[state.loading ? 'visible' : 'invisible', 'mb-1']"
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

        <CrudFormModal
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

        <CrudDeleteModal
          v-if="config.canDelete"
          :open="openDeleteModal"
          :api="api"
          :config="config"
          :item="selectedItem"
          @open="(open: boolean) => (openDeleteModal = open)"
          @deleted="fetch()"
        />

        <CrudPagination
          :config="config"
          :state="state"
          @page="
            (page: number) => {
              state.page = page;
              fetch();
            }
          "
          @page-size="
            (size: number) => {
              state.pageSize = size;
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

const props = defineProps<{ config: CrudConfig }>();
const api = useApi(props.config.endpoint);
const tableRef = ref();
const openCreateModal = ref(false);
const openEditModal = ref(false);
const openDeleteModal = ref(false);
const selectedItem = ref(null);
const mounted = ref(false);

const state = reactive<CrudState>({
  items: [],
  total: 0,
  loading: true,
  page: 1,
  pageSize: props.config.pageSize || 24,
  filters: props.config.defaultFilters
    ? JSON.parse(JSON.stringify(props.config.defaultFilters))
    : {},
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
    })
    .finally(() => {
      state.loading = false;
    });
}

function fetchFirstPage() {
  state.page = 1;
  fetch();
}

onMounted(() => {
  mounted.value = true;
  if (props.config.canRead && props.config.endpoint) {
    fetch();
  }
});

defineExpose({ fetch });
</script>
