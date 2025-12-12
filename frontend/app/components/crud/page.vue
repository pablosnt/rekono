<template>
  <div class="flex flex-col h-full">
    <template v-if="config.canRead">
      <CrudHeader
        :openCreateModal="openCreateModal"
        :config="config"
        :table="tableRef"
        @search="
          (search) => {
            state.searchQuery = search;
            state.page = 1;
            fetch();
          }
        "
        @create="fetch()"
        @openCreateModal="(open) => (openCreateModal = open)"
      />
      <div class="flex-1 overflow-auto">
        <UEmpty
          v-if="state.items.length === 0 && !state.loading"
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
          :config="config"
          :state="state"
          @ordering="
            (sorting) => {
              state.ordering = sorting;
              state.page = 1;
              fetch();
            }
          "
          @tableRef="
            (newTableRef) => {
              tableRef = newTableRef
            }
          "
        />
        <!-- todo: Cards -->
        <!-- TODO: Pagination -->
      </div>
    </template>
    <template v-else>
      <!-- TODO -->
      <!-- <UNotification
        color="danger"
        title="Access denied"
        description="You do not have permission to access this page."
      /> -->
    </template>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState } from "~/types/crud";

const props = defineProps<{ config: CrudConfig<T> }>();
const api = useApi(props.config.endpoint);
const tableRef = ref(null);
const openCreateModal = ref(false);

const state = reactive<CrudState<T>>({
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
    .then((response) => {
      state.items = response.items;
      state.total = response.total;
    })
    .finally(() => {
      state.loading = false;
    });
}

watch([state.page, state.pageSize], () => {
  fetch();
});

onMounted(() => {
  fetch();
});
</script>
