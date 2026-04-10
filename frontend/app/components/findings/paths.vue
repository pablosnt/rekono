<template>
  <Findings
    endpoint="/api/paths/"
    entity-name="Path"
    entity-name-plural="Paths"
    icon="i-lucide-slash"
    :columns="columns"
    :filters="[
      {
        key: 'type',
        label: 'Type',
        icon: 'i-lucide-tag',
        type: 'select',
        options: pathTypes as FilterOption[],
        labelKey: 'value',
      },
    ]"
    :ordering="[
      'id',
      'port',
      { id: 'port__host', label: 'Host' },
      'path',
      'status',
      'type',
    ]"
  />
</template>

<script setup lang="ts">
import type { CrudTableColumn, FilterOption } from "~/types/crud";
import { pathTypes } from "~/constants";

const table = useTable();
const columns: CrudTableColumn<Record<string, unknown>>[] = [
  {
    accessorKey: "host",
    header: "Host",
    icon: "i-lucide-server",
    cell: ({ row }) => {
      const finding = row.original;
      return table.hostCell(finding.port?.host, finding.project);
    },
  },
  {
    accessorKey: "Port",
    header: "Port",
    icon: "i-lucide-ethernet-port",
    cell: ({ row }) => {
      const finding = row.original;
      return table.portCell(finding.port, finding.project);
    },
  },
  {
    accessorKey: "path",
    header: "Path",
    icon: "i-lucide-slash",
    cell: ({ row }) => table.valueCell(row.getValue("path")),
  },
  {
    accessorKey: "type",
    header: "Type",
    icon: "i-lucide-tag",
    cell: ({ row }) => {
      const type = row.getValue("type") as string;
      return table.badgeCell(
        type,
        pathTypes.find((t) => t.value === type)?.icon || "i-lucide-slash",
      );
    },
  },
  {
    accessorKey: "httpStatus",
    header: "HTTP Status",
    icon: "i-lucide-hash",
    cell: ({ row }) => {
      const status = row.getValue("status") as number | null;
      return table.badgeCell(
        status ? status.toString() : status,
        undefined,
        status ? httpStatusColor(status) : "neutral",
      );
    },
  },
  {
    accessorKey: "information",
    header: "Information",
    icon: "i-lucide-info",
    cell: ({ row }) => table.valueCell(row.getValue("extra_info")),
  },
];
</script>
