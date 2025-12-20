<template>
  <div class="flex flex-col h-full w-full">
    <div class="flex-1 overflow-auto">
      <template v-if="config.canRead">
        <div class="container mx-auto max-w-screen-2xl">
          <CrudHeader
            :api="api"
            :open-create-modal="openCreateModal"
            :config="config"
            :state="state"
            :table="tableRef"
            @search="
              (search: string) => {
                state.searchQuery = search;
                fetchFirstPage();
              }
            "
            @filters="
              (filters: Record<string, any>) => {
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
          />

          <UEmpty
            v-if="state.items.length === 0 && !state.loading && Object.keys(state.filters).length === 0 && !state.searchQuery"
            class="mt-10"
            :title="`No ${config.entityNamePlural.toLowerCase()} found`"
            :description="`It looks like you don\'t have access to any ${config.entityName.toLowerCase()} yet. ${config.canCreate ? 'You can create one below.' : 'Please contact your administrator.'}`"
            :icon="config.icon"
            :actions="
              config.canCreate
                ? [
                    {
                      icon: 'i-lucide-plus',
                      label: 'Create new',
                      onClick: () => {
                        openCreateModal = true;
                      },
                    },
                  ]
                : []
            "
            size="xl"
            variant="naked"
          />

          <CrudTable
            v-if="config.tableColumns"
            v-show="state.items.length > 0 || state.loading"
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
          />

          <!-- todo: Cards -->

          <CrudFormModal
            v-if="config.canEdit"
            :open="openEditModal"
            :api="api"
            :config="config"
            :item="selectedItem"
            @open="(open: boolean) => (openEditModal = open)"
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
        </div>
      </template>

      <template v-else>
        <UEmpty
          class="mt-20"
          title="Access Denied"
          description="You do not have the necessary permissions to view this page"
          icon="i-lucide-shield-ban"
          :actions="[
            {
              icon: 'i-lucide-home',
              label: 'Home',
              to: '/',
            },
          ]"
          size="xl"
          variant="naked"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState } from "~/types/crud";

const props = defineProps<{ config: CrudConfig }>();
const api = useApi(props.config.endpoint);
const tableRef = ref(null);
const openCreateModal = ref(false);
const openEditModal = ref(false);
const openDeleteModal = ref(false);
const selectedItem = ref(null);

const state = reactive<CrudState>({
  items: [],
  total: 0,
  loading: true,
  page: 1,
  pageSize: props.config.pageSize || 24,
  filters: {},
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
  if (props.config.canRead) {
    fetch();
  }
});
</script>
