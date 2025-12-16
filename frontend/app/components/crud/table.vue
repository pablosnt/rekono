<template>
  <UTable
    ref="table"
    v-model:column-visibility="config.tableColumnsVisibility"
    :data="state.items"
    :loading="state.loading"
    loading-color="primary"
    :columns="columns"
    class="flex-1"
  />
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState } from "~/types/crud";

const UIcon = resolveComponent("UIcon");
const props = defineProps<{ config: CrudConfig; state: CrudState }>();
const emit = defineEmits<{ edit: [item: any]; delete: [item: any] }>();

const columns = computed(() => {
  const cols =
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
    }) || [];
  cols.push({
    id: "actions",
    enableHiding: false,
    cell: ({ row }: any) => {
      const actions = [];
      const item = row.original;
      if (
        typeof props.config.canEdit === "function"
          ? props.config.canEdit(item)
          : props.config.canEdit
      ) {
        actions.push({
          label: "Edit",
          icon: "i-lucide-pencil",
          onSelect: () => emit("edit", item),
        });
      }
      if (props.config.tableColumns?.some((c) => c.accessorKey === "id")) {
        actions.push({
          label: "Copy ID",
          icon: "i-lucide-copy",
          onSelect: () => {
            navigator.clipboard.writeText(String(item.id));
            const toast = useToast();
            toast.add({ title: "ID copied to clipboard", color: "success" });
          },
        });
      }
      if (
        typeof props.config.canDelete === "function"
          ? props.config.canDelete(item)
          : props.config.canDelete
      ) {
        actions.push({
          label: "Delete",
          icon: "i-lucide-trash",
          color: "error",
          onSelect: () => emit("delete", item),
        });
      }
      if (actions.length === 0) return null;
      return h(
        resolveComponent("UDropdownMenu"),
        {
          items: actions,
          content: { align: "end" },
        },
        () =>
          h(resolveComponent("UButton"), {
            icon: "i-lucide-ellipsis",
            color: "neutral",
            variant: "ghost",
          }),
      );
    },
  });
  return cols;
});

const table = useTemplateRef("table");
defineExpose({ tableApi: computed(() => table.value?.tableApi) });
</script>
