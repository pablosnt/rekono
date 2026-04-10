<template>
  <Findings
    endpoint="/api/technologies/"
    entity-name="Technology"
    entity-name-plural="Technologies"
    icon="i-lucide-layers"
    :columns="columns"
    :ordering="['id', ('port__host', 'Host'), 'port', 'name', 'version']"
    :visibility="{
      description: false,
      credential: false,
      vulnerability: false,
      exploit: false,
    }"
  />
</template>

<script setup lang="ts">
import type { CrudTableColumn } from "~/types/crud";

const route = useRoute();
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
    accessorKey: "port",
    header: "Port",
    icon: "i-lucide-ethernet-port",
    cell: ({ row }) => {
      const finding = row.original;
      return table.portCell(finding.port, finding.project);
    },
  },
  {
    accessorKey: "name",
    header: "Name",
    icon: "i-lucide-case-sensitive",
    cell: ({ row }) => table.valueCell(row.getValue("name")),
  },
  {
    accessorKey: "version",
    header: "Version",
    icon: "i-lucide-tag",
    cell: ({ row }) => table.valueCell(row.getValue("version")),
  },
  {
    accessorKey: "description",
    header: "Description",
    icon: "i-lucide-text",
    cell: ({ row }) => table.valueCell(row.getValue("description")),
  },
  {
    accessorKey: "reference",
    header: "Reference",
    icon: "i-lucide-link",
    cell: ({ row }) =>
      table.externalLinkCell(row.original.reference, "i-lucide-external-link"),
  },
  {
    accessorKey: "credential",
    header: "Credentials",
    icon: "i-lucide-key",
    cell: ({ row }) => {
      const finding = row.original;
      const basePath = `/credentials?technology=${finding.id}`;
      return table.counterCell(
        finding?.credential?.length,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
  {
    accessorKey: "vulnerability",
    header: "Vulnerabilities",
    icon: "i-lucide-bug",
    cell: ({ row }) => {
      const finding = row.original;
      const basePath = `/vulnerabilities?technology=${finding.id}`;
      return table.counterCell(
        finding?.vulnerability?.length,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
  {
    accessorKey: "exploit",
    header: "Exploits",
    icon: "i-lucide-flame",
    cell: ({ row }) => {
      const finding = row.original;
      const basePath = `/exploits?technology=${finding.id}`;
      return table.counterCell(
        finding?.exploit?.length,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
];
</script>
