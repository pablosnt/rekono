<template>
  <div
    v-if="state.total > state.items.length"
    class="flex flex-wrap justify-center lg:justify-between items-center mt-5"
  >
    <div class="flex1 text-sm text-gray-500 mt-3">
      Showing
      <span class="font-medium">{{
        (state.page - 1) * state.pageSize + 1
      }}</span>
      to
      <span class="font-medium">{{
        Math.min(state.page * state.pageSize, state.total)
      }}</span>
      of
      <span class="font-medium">{{ state.total }}</span>
      results
    </div>
    <UPagination
      class="mt-3"
      :model-value="state.page"
      :total="state.total"
      :items-per-page="state.pageSize"
      show-edges
      color="neutral"
      variant="ghost"
      size="lg"
      @update:model-value="(value: number) => $emit('page', value)"
    />
    <div class="flex1 flex items-center gap-2 text-sm text-gray-500 mt-3">
      <span>Items per page</span>
      <USelect
        :model-value="state.pageSize"
        :items="config.pageSizeOptions?.filter((i) => i <= state.total)"
        size="sm"
        @update:model-value="(value: number) => $emit('pageSize', value)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState } from "~/types/crud";

defineProps<{
  config: CrudConfig;
  state: CrudState;
}>();

defineEmits<{
  page: [page: number];
  pageSize: [size: number];
}>();
</script>
