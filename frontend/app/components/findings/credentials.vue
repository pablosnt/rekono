<template>
  <Findings
    endpoint="/api/credentials/"
    entity-name="Credential"
    entity-name-plural="Credentials"
    icon="i-lucide-key"
    :columns="columns"
    :filters="[
      {
        key: 'technology__name__icontains',
        label: 'Technology',
        icon: 'i-lucide-layers',
        type: 'text',
      },
    ]"
    :ordering="['id', 'technology', 'email', 'username', 'secret']"
    is-triageable
  />
</template>

<script setup lang="ts">
import type { CrudTableColumn } from "~/types/crud";

const table = useTable();
const columns: CrudTableColumn<Record<string, unknown>>[] = [
  {
    accessorKey: "host",
    header: "Host",
    icon: "i-lucide-server",
    cell: ({ row }) => {
      const finding = row.original;
      return table.hostCell(finding.technology?.port?.host, finding.project);
    },
  },
  {
    accessorKey: "Port",
    header: "Port",
    icon: "i-lucide-ethernet-port",
    cell: ({ row }) => {
      const finding = row.original;
      return table.portCell(finding.technology?.port, finding.project);
    },
  },
  {
    accessorKey: "technology",
    header: "Technology",
    icon: "i-lucide-layers",
    cell: ({ row }) => {
      const finding = row.original;
      return table.technologyCell(finding.technology, finding.project);
    },
  },
  {
    accessorKey: "email",
    header: "Mail",
    icon: "i-lucide-mail",
    cell: ({ row }) => table.valueCell(row.getValue("email")),
  },
  {
    accessorKey: "username",
    header: "Username",
    icon: "i-lucide-user",
    cell: ({ row }) => table.valueCell(row.getValue("username")),
  },
  {
    accessorKey: "secret",
    header: "Secret",
    icon: "i-lucide-key",
    cell: ({ row }) => table.valueCell(row.getValue("secret")),
  },
  {
    accessorKey: "context",
    header: "Context",
    icon: "i-lucide-message-circle-code",
    cell: ({ row }) => table.valueCell(row.getValue("context")),
  },
];
</script>
