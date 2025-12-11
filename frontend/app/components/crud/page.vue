<template>
  <div class="flex flex-col h-full">
    <template v-if="config.canRead">
      <CrudHeader
        :config="config"
        :table="tableRef"
        @search="
          (search) => {
            state.searchQuery = search;
            state.page = 1;
            fetch();
          }
        "
      />
      <div class="flex-1 overflow-auto">
        <!-- TODO: Loading -->
        <!-- TODO: Empty -->
        <CrudTable
          v-if="config.tableColumns"
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
            (table) => {
              tableRef = table;
            }
          "
        />
        <!-- todo: Cards -->
        <!-- TODO: Pagination -->
      </div>
    </template>
    <template v-else>
      <!-- todo -->
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

const state = reactive<CrudState<T>>({
  items: [],
  total: 0,
  loading: false,
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

// TODO: REMOVE?
// watch([state.searchQuery, state.filters, state.ordering], () => {
//   state.page = 1;
//   fetch();
// });

watch([state.page, state.pageSize], () => {
  fetch();
});

onMounted(() => {
  fetch();
});
</script>
