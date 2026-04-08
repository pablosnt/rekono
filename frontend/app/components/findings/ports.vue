<template>
  <Findings
    endpoint="/api/ports/"
    entity-name="Port"
    entity-name-plural="Ports"
    icon="i-lucide-ethernet-port"
    :columns="columns"
    :filters="[
      {
        key: 'status',
        label: 'Port Status',
        icon: 'i-lucide-chevrons-left-right-ellipsis',
        type: 'select',
        options: portStatuses,
        labelKey: 'value',
      },
      {
        key: 'protocol',
        label: 'Protocol',
        icon: 'i-lucide-network',
        type: 'select',
        options: portProtocols,
      },
    ]"
    :ordering="['id', 'host', 'port', 'status', 'protocol', 'service']"
    :visibility="{ paths: false, technologies: false, vulnerabilities: false }"
  />
</template>

<script setup lang="ts">
import type { CrudTableColumn } from "~/types/crud";
import { portProtocols, portStatuses } from "~/constants";

const route = useRoute();
const table = useTable();
const columns: CrudTableColumn<Record<string, unknown>>[] = [
  {
    accessorKey: "host",
    header: "Host",
    icon: "i-lucide-server",
    cell: ({ row }) => {
      const finding = row.original;
      return table.hostCell(finding.host, finding.project);
    },
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
        row.original.service,
        getPortIcon(row.original.port, row.original.service),
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
      const finding = row.original;
      const basePath = `/paths?port=${finding.id}`;
      return table.counterCell(
        finding?.path?.length,
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
      const finding = row.original;
      const basePath = `/technologies?port=${finding.id}`;
      return table.counterCell(
        finding?.technology?.length,
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
      const finding = row.original;
      const basePath = `/vulnerabilities?port=${finding.id}`;
      return table.counterCell(
        finding?.vulnerability?.length,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
];
</script>
