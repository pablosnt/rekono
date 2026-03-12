<template>
  <UTable
    ref="table"
    :column-visibility="config.tableColumnsVisibility"
    :data="state.items"
    :loading="state.loading"
    loading-color="primary"
    :columns="columns"
    v-on="
      config.itemLink || config.onItemClick
        ? { select: onTableSelect }
        : undefined
    "
  >
    <template #empty>
      <slot name="empty" />
    </template>
  </UTable>
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState } from "~/types/crud";

const UIcon = resolveComponent("UIcon");
const props = defineProps<{ config: CrudConfig; state: CrudState }>();
const emit = defineEmits<{ edit: [item: object]; delete: [item: object] }>();
const slots = useSlots();
const toast = useToast();

const columns = computed(() => {
  const cols =
    props.config.tableColumns?.map((column: unknown) => {
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
    cell: ({ row }: unknown) => {
      const actions = [];
      const item = row.original;

      if (props.config.customDropdownActions) {
        const customActions = props.config.customDropdownActions(item);
        customActions.forEach((action) => {
          actions.push({
            label: action.label,
            icon: action.icon,
            color: action.color,
            onSelect: () => action.onSelect(item),
          });
        });
      }

      if (
        props.config.tableCopyId !== false &&
        props.config.tableColumns?.some((c) => c.accessorKey === "id")
      ) {
        actions.push({
          label: "Copy ID",
          icon: "i-lucide-copy",
          onSelect: () => {
            navigator.clipboard.writeText(String(item.id));
            toast.add({ title: "ID copied to clipboard", color: "success" });
          },
        });
      }
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
      const elements = [];
      if (slots.actions) {
        elements.push(slots.actions({ item }));
      }
      if (actions.length > 0) {
        elements.push(
          h(
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
          ),
        );
      }
      if (elements.length === 0) return null;
      return h("div", { class: "flex items-center gap-2" }, elements);
    },
  });
  return cols;
});

function onTableSelect(event: unknown, row: unknown) {
  if (props.config.itemLink) {
    navigateTo(props.config.itemLink(row.original));
  } else if (props.config.onItemClick) {
    props.config.onItemClick(row.original);
  }
}

const table = useTemplateRef("table");
defineExpose({ tableApi: computed(() => table.value?.tableApi) });
</script>
