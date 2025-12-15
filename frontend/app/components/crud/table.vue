<template>
  <UContainer>
    <UTable
      ref="table"
      :data="state.items"
      :loading="state.loading"
      loading-color="primary"
      :columns="columns"
      v-model:column-visibility="config.tableColumnsVisibility"
      class="flex-1"
    />
  </UContainer>
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState } from "~/types/crud";
const UIcon = resolveComponent("UIcon");

const props = defineProps<{ config: CrudConfig; state: CrudState }>();

const columns = computed(() =>
  props.config.tableColumns?.map((column: any) => {
    return column.icon
      ? {
          ...column,
          header: h("div", { class: "flex items-center gap-1.5" }, [
            h(UIcon, {
              name: column.icon,
              class: "w-4 h-4 text-gray-500 dark:text-gray-400",
            }),
            h("span", column.header as string),
          ]),
        }
      : column;
  }),
);

const table = useTemplateRef("table");
defineExpose({ tableApi: computed(() => table.value?.tableApi) });
// TODO: Actions -> Edit & Delete -> https://ui.nuxt.com/docs/components/table#with-slots
</script>
