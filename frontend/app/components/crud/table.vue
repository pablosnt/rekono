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

const props = defineProps<{ config: CrudConfig; state: CrudState }>();
const emit = defineEmits<{
  tableRef: [newTableRef: any];
  ordering: [ordering: string];
}>();

const UDropdownMenu = resolveComponent("UDropdownMenu");
const UButton = resolveComponent("UButton");
const UIcon = resolveComponent("UIcon");

const columns = computed(() =>
  props.config.tableColumns?.map((column: any) => {
    if (!props.config.ordering?.includes(column.accessorKey)) {
        return column.icon ? {
          ...column,
          header: h("div", { class: "flex items-center gap-1.5" }, [
            h(UIcon, {
              name: column.icon,
              class: "w-4 h-4 text-gray-500 dark:text-gray-400",
            }),
            h("span", column.header as string),
          ]),
        } : column;
    }
    let sorted = null;
    if (props.state.ordering) {
      if (props.state.ordering.includes(column.accessorKey)) {
        sorted = props.state.ordering.startsWith("-") ? "desc" : "asc";
      }
    }
    return {
      ...column,
      header: h(
        UDropdownMenu,
        {
          content: {
            align: "start",
          },
          "aria-label": "Ordering dropdown",
          items: [
            {
              label: "Asc",
              type: "checkbox",
              icon: "i-lucide-arrow-up-narrow-wide",
              checked: sorted === "asc",
              onSelect: () => {
                if (sorted === "asc") {
                  emit("ordering", props.config.defaultOrdering);
                } else {
                  emit("ordering", column.accessorKey);
                }
              },
            },
            {
              label: "Desc",
              icon: "i-lucide-arrow-down-wide-narrow",
              type: "checkbox",
              checked: sorted === "desc",
              onSelect: () => {
                if (sorted === "desc") {
                  emit("ordering", props.config.defaultOrdering);
                } else {
                  emit("ordering", `-${column.accessorKey}`);
                }
              },
            },
          ],
        },
        () =>
          h(UButton, {
            color: "neutral",
            variant: "ghost",
            label: column.header as string,
            icon: sorted
              ? sorted === "asc"
                ? "i-lucide-arrow-up-narrow-wide"
                : "i-lucide-arrow-down-wide-narrow"
              : column.icon ? column.icon : "i-lucide-arrow-up-down",
            class: "-mx-2.5 data-[state=open]:bg-elevated",
            "aria-label": `Sort by ${sorted === "asc" ? "ascending" : "descending"}`,
          }),
      ),
    };
  }),
);

const table = useTemplateRef("table");

onMounted(() => {
  emit("tableRef", table.value);
});
// TODO: Actions -> Edit & Delete -> https://ui.nuxt.com/docs/components/table#with-slots
</script>
