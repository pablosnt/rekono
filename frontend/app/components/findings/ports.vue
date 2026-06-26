<template>
  <FindingsMultiple
    endpoint="/api/ports/"
    entity-name="Port"
    entity-name-plural="Ports"
    icon="i-lucide-ethernet-port"
    :columns="columns"
    :filters="filters"
    :ordering="
      [
        'id',
        host ? undefined : 'host',
        'port',
        'status',
        'protocol',
        'service',
      ].filter((i) => Boolean(i))
    "
    :visibility="{ paths: false, technologies: false, vulnerabilities: false }"
    :custom-default-filters="host ? { host: host } : undefined"
    is-asset
    has-hacktricks
    :disable-url-sync="disableUrlSync"
  />
</template>

<script setup lang="ts">
import type { CrudTableColumn } from "~/types/crud";
import { portProtocols, portStatuses } from "~/constants";
import type { Port } from "~/types/models";

const props = defineProps<{
  host?: number;
  disableUrlSync?: boolean;
}>();

const route = useRoute();
const table = useTable();
const options = useOptions();
const hostOptions = ref();
const filters = computed(() =>
  [
    props.host
      ? {}
      : {
          key: "host",
          label: "Host",
          icon: "i-lucide-server",
          type: "select" as const,
          options: hostOptions,
        },
    {
      key: "status",
      label: "Port Status",
      icon: "i-lucide-chevrons-left-right-ellipsis",
      type: "select",
      options: portStatuses,
      labelKey: "value",
    },
    {
      key: "protocol",
      label: "Protocol",
      icon: "i-lucide-network",
      type: "select",
      options: portProtocols,
    },
  ].filter((f) => Object.keys(f).length > 0),
);
const columns: CrudTableColumn<Port>[] = [
  props.host
    ? {}
    : {
        accessorKey: "host",
        header: "Host",
        icon: "i-lucide-server",
        cell: ({ row }) =>
          table.hostCell(row.original.host, row.original.project),
      },
  {
    accessorKey: "port",
    header: "Port",
    icon: "i-lucide-ethernet-port",
    cell: ({ row }) => table.valueCell(String(row.original.port)),
  },
  {
    accessorKey: "protocol",
    header: "Protocol",
    icon: "i-lucide-network",
    cell: ({ row }) => table.badgeCell(row.getValue("protocol")),
  },
  {
    accessorKey: "service",
    header: "Service",
    icon: "i-lucide-layers",
    cell: ({ row }) =>
      table.iconAndValueCell(
        getPortIcon(row.original.port, row.original.service),
        row.original.service,
      ),
  },
  {
    accessorKey: "portStatus",
    header: "Port Status",
    icon: "i-lucide-chevrons-left-right-ellipsis",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      const config = portStatuses.find((s) => s.value === status);
      return table.badgeCell(status, config?.icon, config?.color);
    },
  },
  {
    accessorKey: "paths",
    header: "Paths",
    icon: "i-lucide-slash",
    cell: ({ row }) => {
      const basePath = `/paths?port=${row.original.id}`;
      return table.counterCell(
        row.original?.path?.length,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
  {
    accessorKey: "technologies",
    header: "Technologies",
    icon: "i-lucide-layers",
    cell: ({ row }) => {
      const basePath = `/technologies?port=${row.original.id}`;
      return table.counterCell(
        row.original?.technology?.length,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
  {
    accessorKey: "vulnerabilities",
    header: "Vulnerabilities",
    icon: "i-lucide-bug",
    cell: ({ row }) => {
      const basePath = `/vulnerabilities?port=${row.original.id}`;
      return table.counterCell(
        row.original?.vulnerability?.length,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
].filter((c) => Object.keys(c).length > 0);

onMounted(() => {
  options.hosts(
    hostOptions,
    route.params.project_id ? { project: route.params.project_id } : {},
  );
});
</script>
