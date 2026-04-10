<template>
  <Findings
    endpoint="/api/vulnerabilities/"
    entity-name="Vulnerability"
    entity-name-plural="Vulnerabilities"
    icon="i-lucide-bug"
    :columns="columns"
    :filters="[
      {
        key: 'severity',
        label: 'Severity',
        icon: 'i-lucide-shield',
        type: 'select',
        options: severities,
        labelKey: 'value',
      },
      {
        key: 'trending',
        label: 'Trending',
        icon: 'i-lucide-trending-up',
        type: 'boolean',
      },
    ]"
    :ordering="[
      'id',
      'technology',
      'port',
      'name',
      'severity',
      ('cve', 'CVE'),
      ('cwe', 'CWE'),
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
import type { Finding } from "~/types/models";

const route = useRoute();
const table = useTable();
const toast = useToast();

const columns: CrudTableColumn<Record<string, unknown>>[] = [
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
      if (row.original.trending) {
        return cve
          ? h("div", { class: "flex items-center gap-2" }, [
              h(
                UTooltip,
                { text: "Trending" },
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
          : table.noDataCell;
      } else {
        return table.valueCell(cve);
      }
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
      table.externalLinkCell(
        row.original.reference as string | undefined,
        "i-lucide-external-link",
        undefined,
      ),
  },
  {
    accessorKey: "exploit",
    header: "Exploits",
    icon: "i-lucide-flame",
    cell: ({ row }) => {
      const finding = row.original;
      const basePath = `/exploits?vulnerability=${finding.id}`;
      return table.counterCell(
        finding.exploit?.length || 0,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
];

function dropdownActions(item: Finding) {
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
</script>
