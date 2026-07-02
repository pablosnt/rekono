<template>
  <FindingsMultiple
    endpoint="/api/vulnerabilities/"
    entity-name="Vulnerability"
    entity-name-plural="Vulnerabilities"
    icon="i-lucide-bug"
    :columns="columns"
    :filters="filters"
    :accepted-filters="acceptedFilters"
    :ordering="[
      'id',
      ...(port || technology ? [] : ['technology', 'port']),
      'name',
      'severity',
      { id: 'cvss_base_score', label: 'CVSS' },
      { id: 'cve', label: 'CVE' },
      { id: 'euvd_id', label: 'EUVD' },
      { id: 'ghsa_id', label: 'GHSA' },
      { id: 'osv_generic_id', label: 'OSV' },
      { id: 'cwes', label: 'CWE' },
      { id: 'epss_score', label: 'EPSS' },
    ]"
    default-ordering="-severity,-id"
    :visibility="{
      description: false,
      euvd_id: false,
      ghsa_id: false,
      osv_generic_id: false,
      epss_percentile: false,
    }"
    :extra-dropdown-actions="dropdownActions"
    :custom-default-filters="
      port
        ? { port: port }
        : technology
          ? { technology: technology }
          : undefined
    "
    is-triageable
    :disable-url-sync="disableUrlSync"
    :link-to-original-page="linkToOriginalPage"
  />
</template>

<script setup lang="ts">
import { h, resolveComponent } from "vue";
import { UTooltip, UButton, UIcon } from "#components";
import type { CrudTableColumn } from "~/types/crud";
import { severities } from "~/constants";
import type { Vulnerability } from "~/types/models";

const props = defineProps<{
  port?: number;
  technology?: number;
  disableUrlSync?: boolean;
  linkToOriginalPage?: string;
}>();

const route = useRoute();
const table = useTable();
const options = useOptions();
const acceptedFilters = computed(() =>
  props.port || props.technology
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
          loadOption: (value: string | number) => options.technology(value),
        },
      ],
);
const filters = computed(() => [
  {
    key: "severity",
    label: "Severity",
    icon: "i-lucide-shield",
    type: "select",
    options: severities,
    labelKey: "value",
  },
  {
    key: "cwe",
    label: "CWE",
    icon: "i-lucide-tag",
    type: "text",
    placeholder: "Filter by CWE...",
  },
  {
    key: "trending",
    label: "Trending",
    icon: "i-lucide-trending-up",
    type: "checkbox",
  },
]);
const columns: CrudTableColumn<Vulnerability>[] = [
  ...(props.port || props.technology
    ? []
    : [
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
      ]),
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
    accessorKey: "cvss",
    header: "CVSS",
    icon: "i-lucide-gauge",
    cell: ({ row }) => {
      const score = row.original.cvss_base_score as number | undefined;
      if (!score) return table.noDataCell;
      return row.original.cvss_vector && row.original.cvss_version
        ? table.externalLinkCell(
            `https://www.first.org/cvss/calculator/${row.original.cvss_version}#${row.original.cvss_vector}`,
            undefined,
            undefined,
            score.toPrecision(3),
            "Open CVSS Calculator",
          )
        : table.valueCell(score.toPrecision(3));
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
                  text: "Trending on CVECrowd",
                  content: { side: "left", sideOffset: 8, collisionPadding: 8 },
                },
                {
                  default: () =>
                    h(
                      UButton,
                      {
                        target: "_blank",
                        to: "https://cvecrowd.com/",
                        color: "neutral",
                        variant: "ghost",
                        "aria-label": "Trending on CVECrowd",
                      },
                      [
                        h(UIcon, {
                          name: "i-lucide-trending-up",
                          class: "text-orange text-xl shrink-0",
                          "aria-hidden": "true",
                        }),
                      ],
                    ),
                },
              ),
              table.valueCell(cve),
            ])
          : table.noDataCell
        : table.valueCell(cve);
    },
  },
  {
    accessorKey: "euvd_id",
    header: "EUVD ID",
    icon: "i-lucide-hash",
    cell: ({ row }) =>
      row.original.euvd_id
        ? table.valueCell(row.original.euvd_id)
        : table.noDataCell,
  },
  {
    accessorKey: "ghsa_id",
    header: "GHSA ID",
    icon: "i-lucide-hash",
    cell: ({ row }) =>
      row.original.ghsa_id
        ? table.valueCell(row.original.ghsa_id)
        : table.noDataCell,
  },
  {
    accessorKey: "osv_generic_id",
    header: "OSV ID",
    icon: "i-lucide-hash",
    cell: ({ row }) =>
      row.original.osv_generic_id
        ? table.valueCell(row.original.osv_generic_id)
        : table.noDataCell,
  },
  {
    accessorKey: "cwes",
    header: "CWE",
    icon: "i-lucide-tag",
    cell: ({ row }) =>
      row.original.cwes?.length
        ? h(resolveComponent("Tags"), { tags: row.original.cwes })
        : table.noDataCell,
  },
  {
    accessorKey: "epss_score",
    header: "EPSS",
    icon: "i-lucide-brain-circuit",
    cell: ({ row }) =>
      row.original.epss_score
        ? table.valueCell(`${row.original.epss_score.toPrecision(4)}%`)
        : table.noDataCell,
  },
  {
    accessorKey: "epss_percentile",
    header: "EPSS Percentile",
    icon: "i-lucide-brain-circuit",
    cell: ({ row }) =>
      row.original.epss_percentile
        ? table.valueCell(`${row.original.epss_percentile.toPrecision(4)}%`)
        : table.noDataCell,
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
];

function dropdownActions(item: Vulnerability) {
  return [
    ...(item.cve
      ? [
          {
            label: "Copy CVE",
            icon: "i-lucide-hash",
            onSelect: () => copyText(item.cve, "CVE copied to clipboard"),
          },
        ]
      : []),
    ...(item.cve
      ? [
          {
            label: "Copy CVE",
            icon: "i-lucide-hash",
            onSelect: () => copyText(item.cve, "CVE copied to clipboard"),
          },
        ]
      : []),
    ...(item.euvd_id
      ? [
          {
            label: "Copy EUVD ID",
            icon: "i-lucide-hash",
            onSelect: () =>
              copyText(item.euvd_id, "EUVD ID copied to clipboard"),
          },
        ]
      : []),
    ...(item.ghsa_id
      ? [
          {
            label: "Copy GHSA ID",
            icon: "i-lucide-hash",
            onSelect: () =>
              copyText(item.ghsa_id, "GHSA ID copied to clipboard"),
          },
        ]
      : []),
    ...(item.osv_generic_id
      ? [
          {
            label: "Copy OSV ID",
            icon: "i-lucide-hash",
            onSelect: () =>
              copyText(item.osv_generic_id, "OSV ID copied to clipboard"),
          },
        ]
      : []),
    ...(item.cvss_vector
      ? [
          {
            label: "Copy CVSS vector",
            icon: "i-lucide-gauge",
            onSelect: () =>
              copyText(item.cvss_vector, "CVSS vector copied to clipboard"),
          },
        ]
      : []),
  ];
}
</script>
