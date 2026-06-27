<template>
  <FindingsMultiple
    endpoint="/api/credentials/"
    entity-name="Credential"
    entity-name-plural="Credentials"
    icon="i-lucide-key"
    :columns="columns"
    :accepted-filters="acceptedFilters"
    :ordering="[
      'id',
      ...(technology ? [] : ['technology']),
      'email',
      'username',
      'secret',
    ]"
    :custom-default-filters="
      technology ? { technology: technology } : undefined
    "
    :disable-url-sync="disableUrlSync"
    is-triageable
  />
</template>

<script setup lang="ts">
import type { CrudTableColumn } from "~/types/crud";
import type { Credential } from "~/types/models";

const props = defineProps<{
  technology?: number;
  disableUrlSync?: boolean;
}>();

const table = useTable();
const options = useOptions();
const acceptedFilters = computed(() =>
  props.technology
    ? []
    : [
        {
          key: "host",
          label: "Host",
          icon: "i-lucide-server",
          loadOption: (value: string | number) => options.host(value),
        },
        {
          key: "port",
          label: "Port",
          icon: "i-lucide-ethernet-port",
          loadOption: (value: string | number) => options.port(value),
        },
        {
          key: "technology",
          label: "Technology",
          icon: "i-lucide-layers",
          loadOption: (value: string | number) =>
            options.technology(value),
        },
      ],
);
const columns: CrudTableColumn<Credential>[] = [
  ...(props.technology
    ? []
    : [
        {
          accessorKey: "host",
          header: "Host",
          icon: "i-lucide-server",
          cell: ({ row }) =>
            table.hostCell(
              row.original.technology?.port?.host,
              row.original.project,
            ),
        },
        {
          accessorKey: "Port",
          header: "Port",
          icon: "i-lucide-ethernet-port",
          cell: ({ row }) =>
            table.portCell(row.original.technology?.port, row.original.project),
        },
        {
          accessorKey: "technology",
          header: "Technology",
          icon: "i-lucide-layers",
          cell: ({ row }) =>
            table.technologyCell(row.original.technology, row.original.project),
        },
      ]),
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
