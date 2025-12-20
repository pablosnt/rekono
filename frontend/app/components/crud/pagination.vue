<template>
  <div
    v-if="state.total > state.items.length"
    class="grid grid-cols-3 items-center mt-5 px-3"
  >
    <div class="text-sm text-gray-500">
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
    <div class="flex justify-center">
      <UPagination
        :model-value="state.page"
        :total="state.total"
        :items-per-page="state.pageSize"
        show-edges
        color="neutral"
        variant="ghost"
        size="lg"
        @update:model-value="(value: number) => $emit('page', value)"
      />
    </div>
    <div class="flex justify-end items-center gap-2 text-sm text-gray-500">
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
