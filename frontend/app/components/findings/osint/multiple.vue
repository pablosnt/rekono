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
    is-triageable
    :extra-dropdown-actions="
      (item: OSINT) =>
        ['IP', 'Domain'].includes(item.data_type)
          ? [
              {
                label: 'Create target',
                icon: 'i-lucide-locate-fixed',
                color: 'error',
                onSelect: (item) => {
                  api
                    .create(`${item.id}/target/`, {}, {}, 'Target')
                    .then((response) =>
                      navigateTo(
                        `/projects/${response.project}/targets/${response.id}`,
                      ),
                    );
                },
              },
            ]
          : []
    "
  />
</template>

<script setup lang="ts">
import type { CrudTableColumn, FilterOption } from "~/types/crud";
import { osintDataTypes } from "~/constants";
import type { OSINT } from "~/types/models";

const api = useApi("/api/osint/");
const table = useTable();
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
