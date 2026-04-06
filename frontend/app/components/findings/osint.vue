<template>
  <Findings
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
        options: backend.osintDataTypes as FilterOption[],
        labelKey: 'value',
      },
    ]"
    :ordering="['id', 'data', ('data_type', 'Type'), 'source']"
    is-triageable
    :extra-dropdown-actions="
      (item: Finding) =>
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
import { h } from "vue";
import type { CrudTableColumn, FilterOption } from "~/types/crud";

const api = useApi("/api/osint/");
const backend = useBackend();
const columns: CrudTableColumn<Record<string, unknown>>[] = [
  {
    accessorKey: "data",
    header: "Data",
    icon: "i-lucide-database-search",
    cell: ({ row }) =>
      h("span", { class: "font-medium" }, row.getValue("data")),
  },
  {
    accessorKey: "type",
    header: "Type",
    icon: "i-lucide-tag",
    cell: ({ row }) => {
      const type = row.original.data_type as string;
      const config = backend.osintDataTypes.find((t) => t.value === type);
      return h(
        resolveComponent("UBadge"),
        { color: "neutral", variant: "subtle" },
        {
          default: () => [
            h(resolveComponent("UIcon"), {
              name: config?.icon || "i-lucide-rss",
              class: "mr-1 text-lg",
            }),
            type,
          ],
        },
      );
    },
  },
  {
    accessorKey: "source",
    header: "Source",
    icon: "i-lucide-search",
    cell: ({ row }) => {
      const source = row.getValue("source") as string;
      if (!source) return null;
      return h("span", { class: "text-sm" }, source);
    },
  },
];
</script>
