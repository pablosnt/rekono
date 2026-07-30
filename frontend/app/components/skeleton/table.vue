<template>
  <CrudTable
    aria-hidden="true"
    :config="skeletonConfig"
    :state="skeletonState"
  />
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState } from "~/types/crud";

const props = withDefaults(
  defineProps<{ config: CrudConfig; count?: number }>(),
  { count: 6 },
);
const skeletonConfig = computed<CrudConfig>(() => ({
  ...props.config,
  tableColumns: props.config.tableColumns?.map((column) => ({
    ...column,
    cell: () => h(resolveComponent("USkeleton"), { class: "h-5 w-24" }),
  })),
  canEdit: false,
  canDelete: false,
  tableCopyId: false,
  customDropdownActions: undefined,
}));
const skeletonState = computed<CrudState>(() => ({
  items: Array.from({ length: props.count }, (_, index) => ({ id: index })),
  total: props.count,
  loading: false,
  page: 1,
  pageSize: props.count,
  filters: {},
  ordering: "",
}));
</script>
