<template>
  <FindingsMultiple
    endpoint="/api/vulnerabilities/"
    entity-name="Vulnerability"
    entity-name-plural="Vulnerabilities"
    icon="i-lucide-bug"
    :columns="columns"
    :filters="filters"
    :ordering="[
      'id',
      'technology',
      'port',
      'name',
      'severity',
      { id: 'cve', label: 'CVE' },
      { id: 'cwe', label: 'CWE' },
    ]"
    :visibility="{
      description: false,
    }"
    :extra-dropdown-actions="dropdownActions"
    is-triageable
  />
</template>

<script setup lang="ts">
import { h } from "vue";
import { UTooltip, UIcon } from "#components";
import type { CrudTableColumn } from "~/types/crud";
import { severities } from "~/constants";
import type { Vulnerability } from "~/types/models";

const toast = useToast();
const route = useRoute();
const table = useTable();
const options = useOptions();
const hostOptions = ref();
const portOptions = ref();
const technologyOptions = ref();
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
  {
    key: "technology",
    label: "Technology",
    icon: "i-lucide-layers",
    type: "select" as const,
    options: technologyOptions,
  },
  {
    key: "severity",
    label: "Severity",
    icon: "i-lucide-shield",
    type: "select",
    options: severities,
    labelKey: "value",
  },
  {
    key: "trending",
    label: "Trending",
    icon: "i-lucide-trending-up",
    type: "checkbox",
  },
]);
const columns: CrudTableColumn<Vulnerability>[] = [
  {
    accessorKey: "host",
    header: "Host",
    icon: "i-lucide-server",
    cell: ({ row }) =>
      table.hostCell(
        row.original.port?.host || row.original.technology?.port?.host,
        row.original.project,
      ),
  },
  {
    accessorKey: "port",
    header: "Port",
    icon: "i-lucide-ethernet-port",
    cell: ({ row }) =>
      table.portCell(
        row.original.port || row.original.technology?.port,
        row.original.project,
      ),
  },
  {
    accessorKey: "technology",
    header: "Technology",
    icon: "i-lucide-layers",
    cell: ({ row }) =>
      table.technologyCell(row.original.technology, row.original.project),
  },
  {
    accessorKey: "name",
    header: "Name",
    icon: "i-lucide-case-sensitive",
    cell: ({ row }) => table.valueCell(row.getValue("name")),
  },
  {
    accessorKey: "description",
    header: "Description",
    icon: "i-lucide-text",
    cell: ({ row }) => table.valueCell(row.getValue("description")),
  },
  {
    accessorKey: "severity",
    header: "Severity",
    icon: "i-lucide-shield-alert",
    cell: ({ row }) => {
      const value = row.getValue("severity") as string | undefined;
      const severity = severities.find((s) => s.value === value);
      return table.badgeCell(value, severity?.icon, severity?.color);
    },
  },
  {
    accessorKey: "cvss_base_score",
    header: "CVSS",
    icon: "i-lucide-gauge",
    cell: ({ row }) => {
      const score = row.original.cvss_base_score as number | undefined;
      return score ? table.valueCell(score.toPrecision(3)) : table.noDataCell;
    },
  },
  {
    accessorKey: "cve",
    header: "CVE",
    icon: "i-lucide-hash",
    cell: ({ row }) => {
      const cve = row.original.cve as string | undefined;
      return row.original.trending
        ? cve
          ? h("div", { class: "flex items-center gap-2" }, [
              h(
                UTooltip,
                {
                  text: "Trending",
                  content: { side: "left", sideOffset: 8, collisionPadding: 8 },
                },
                {
                  default: () =>
                    h(UIcon, {
                      name: "i-lucide-trending-up",
                      class: "text-warning text-lg shrink-0",
                    }),
                },
              ),
              table.valueCell(cve),
            ])
          : table.noDataCell
        : table.valueCell(cve);
    },
  },
  {
    accessorKey: "cwe",
    header: "CWE",
    icon: "i-lucide-tag",
    cell: ({ row }) => table.valueCell(row.getValue("cwe")),
  },
  {
    accessorKey: "reference",
    header: "Reference",
    icon: "i-lucide-link",
    cell: ({ row }) =>
      table.externalLinkCell(row.original.reference, "i-lucide-external-link"),
  },
  {
    accessorKey: "exploit",
    header: "Exploits",
    icon: "i-lucide-flame",
    cell: ({ row }) => {
      const basePath = `/exploits?vulnerability=${row.original.id}`;
      return table.counterCell(
        row.original.exploit?.length || 0,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
];

function dropdownActions(item: Vulnerability) {
  return [
    item.cve
      ? {
          label: "Copy CVE",
          icon: "i-lucide-hash",
          onSelect: () => {
            navigator.clipboard.writeText(item.cve);
            toast.add({
              title: "CVE copied to clipboard",
              color: "success",
              icon: "i-lucide-clipboard-check",
            });
          },
        }
      : {},
    item.cvss_vector
      ? {
          label: "Copy CVSS vector",
          icon: "i-lucide-gauge",
          onSelect: () => {
            navigator.clipboard.writeText(item.cvss_vector);
            toast.add({
              title: "CVSS vector copied to clipboard",
              color: "success",
              icon: "i-lucide-clipboard-check",
            });
          },
        }
      : {},
  ].filter((i) => Object.keys(i).length > 0);
}

onMounted(() => {
  const query = route.params.project_id
    ? { project: route.params.project_id }
    : {};
  options.hosts(hostOptions, query);
  options.ports(portOptions, query);
  options.technologies(technologyOptions, query);
});
</script>
