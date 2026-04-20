<template>
  <FindingsMultiple
    endpoint="/api/osint/"
    entity-name="OSINT"
    entity-name-plural="OSINT"
    icon="i-lucide-rss"
    :columns="columns"
    :filters="[
      {
        key: 'data_type',
        label: 'Type',
        icon: 'i-lucide-tag',
        type: 'select',
        options: osintDataTypes as FilterOption[],
        labelKey: 'value',
      },
    ]"
    :ordering="['id', 'data', { id: 'data_type', label: 'Type' }, 'source']"
    :extra-dropdown-actions="
      (item: OSINT) =>
        userStore.is_auditor && ['IP', 'Domain'].includes(item.data_type)
          ? [getOSINTDropdownActions(item, api)]
          : []
    "
    is-triageable
    custom-fix-verb="Discard"
  />
</template>

<script setup lang="ts">
import type { CrudTableColumn, FilterOption } from "~/types/crud";
import { osintDataTypes } from "~/constants";
import type { OSINT } from "~/types/models";
import { useUserStore } from "~/store/user";

const api = useApi("/api/osint/");
const table = useTable();
const userStore = useUserStore();
const columns: CrudTableColumn<OSINT>[] = [
  {
    accessorKey: "data",
    header: "Data",
    icon: "i-lucide-database-search",
    cell: ({ row }) => table.valueCell(row.getValue("data")),
  },
  {
    accessorKey: "type",
    header: "Type",
    icon: "i-lucide-tag",
    cell: ({ row }) => {
      const type = row.original.data_type;
      return table.badgeCell(
        type,
        osintDataTypes.find((t) => t.value === type)?.icon || "i-lucide-rss",
      );
    },
  },
  {
    accessorKey: "source",
    header: "Source",
    icon: "i-lucide-search",
    cell: ({ row }) => table.valueCell(row.getValue("source")),
  },
];
</script>
