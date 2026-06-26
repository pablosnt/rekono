<template>
  <FindingsMultiple
    endpoint="/api/technologies/"
    entity-name="Technology"
    entity-name-plural="Technologies"
    icon="i-lucide-layers"
    :columns="columns"
    :filters="filters"
    :ordering="[
      'id',
      ...(port ? [] : [{ id: 'port__host', label: 'Host' }, 'port']),
      'name',
      'version',
    ]"
    :visibility="{
      description: false,
      credential: false,
      vulnerability: false,
      exploit: false,
    }"
    :custom-default-filters="port ? { port: port } : undefined"
    is-asset
    has-hacktricks
    :disable-url-sync="disableUrlSync"
  />
</template>

<script setup lang="ts">
import type { CrudTableColumn } from "~/types/crud";
import type { Technology } from "~/types/models";

const props = defineProps<{
  port?: number;
  disableUrlSync?: boolean;
}>();

const route = useRoute();
const table = useTable();
const options = useOptions();
const hostOptions = ref();
const portOptions = ref();
const filters = computed(() =>
  props.port
    ? []
    : [
        {
          key: "port__host",
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
      ],
);
const columns: CrudTableColumn<Technology>[] = [
  ...(props.port
    ? []
    : [
        {
          accessorKey: "host",
          header: "Host",
          icon: "i-lucide-server",
          cell: ({ row }) =>
            table.hostCell(row.original.port?.host, row.original.project),
        },
        {
          accessorKey: "port",
          header: "Port",
          icon: "i-lucide-ethernet-port",
          cell: ({ row }) =>
            table.portCell(row.original.port, row.original.project),
        },
      ]),
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
      table.externalLinkCell(
        row.original.reference,
        "i-lucide-external-link",
        undefined,
        undefined,
        "Reference",
      ),
  },
  {
    accessorKey: "credential",
    header: "Credentials",
    icon: "i-lucide-key",
    cell: ({ row }) => {
      const basePath = `/credentials?technology=${row.original.id}`;
      return table.counterCell(
        row.original?.credential?.length,
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
      const basePath = `/vulnerabilities?technology=${row.original.id}`;
      return table.counterCell(
        row.original?.vulnerability?.length,
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
      const basePath = `/exploits?technology=${row.original.id}`;
      return table.counterCell(
        row.original?.exploit?.length,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
];

onMounted(() => {
  if (props.port) return;
  const query = route.params.project_id
    ? { project: route.params.project_id }
    : {};
  options.hosts(hostOptions, query);
  options.ports(portOptions, query);
});
</script>
