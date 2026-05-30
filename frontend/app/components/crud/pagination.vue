<template>
  <div
    v-if="state.total > Math.min(state.items.length, ...config.pageSizeOptions)"
    class="flex flex-wrap md:flex-row flex-col justify-between items-center mt-5"
  >
    <div class="text-sm text-gray-500 mt-3">
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
      :page="state.page"
      :total="state.total"
      :items-per-page="state.pageSize"
      show-edges
      color="neutral"
      variant="ghost"
      size="lg"
      @update:page="(value: number) => $emit('page', value)"
    />
    <div class="flex items-center gap-2 text-sm text-gray-500 mt-3">
      <span>Items per page</span>
      <USelect
        :model-value="state.pageSize"
        :items="config.pageSizeOptions"
        size="sm"
        aria-label="Items per page"
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
