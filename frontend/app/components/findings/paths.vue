<template>
  <Findings
    endpoint="/api/paths/"
    entity-name="Path"
    entity-name-plural="Paths"
    icon="i-lucide-slash"
    :columns="columns"
    :filters="filters"
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
import type { CrudTableColumn } from "~/types/crud";
import { pathTypes } from "~/constants";
import type { Path } from "~/types/models";

const route = useRoute();
const table = useTable();
const options = useOptions();
const hostOptions = ref();
const portOptions = ref();
const filters = computed(() => [
  {
    key: "host",
    label: "Host",
    icon: "i-lucide-server",
    type: "select" as const,
    options: hostOptions,
  },
  {
    key: "port",
    label: "Port",
    icon: "i-lucide-ethernet-port",
    type: "select" as const,
    options: portOptions,
  },
]);
const columns: CrudTableColumn<Path>[] = [
  {
    accessorKey: "host",
    header: "Host",
    icon: "i-lucide-server",
    cell: ({ row }) =>
      table.hostCell(row.original.port?.host, row.original.project),
  },
  {
    accessorKey: "Port",
    header: "Port",
    icon: "i-lucide-ethernet-port",
    cell: ({ row }) => table.portCell(row.original.port, row.original.project),
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
    cell: ({ row }) =>
      table.badgeCell(
        row.original.type,
        pathTypes.find((t) => t.value === row.original.type)?.icon ||
          "i-lucide-slash",
      ),
  },
  {
    accessorKey: "httpStatus",
    header: "HTTP Status",
    icon: "i-lucide-hash",
    cell: ({ row }) => {
      const status = row.getValue("status") as number | null;
      return table.badgeCell(
        status ? status.toString() : undefined,
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

onMounted(() => {
  const query = route.params.project_id
    ? { project: route.params.project_id }
    : {};
  options.hosts(hostOptions, query);
  options.ports(portOptions, query);
});
</script>
