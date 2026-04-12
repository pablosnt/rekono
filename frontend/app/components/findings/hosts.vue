<template>
  <div>
    <Findings
      endpoint="/api/hosts/"
      entity-name="Host"
      entity-name-plural="Hosts"
      icon="i-lucide-server"
      :columns="columns"
      :filters="[
        {
          key: 'os_type',
          label: 'OS',
          icon: 'i-lucide-monitor',
          type: 'select',
          options: hostOS,
          labelKey: 'value',
        },
      ]"
      :ordering="[
        'id',
        'ip',
        'domain',
        { id: 'os_type', label: 'OS' },
        'country',
        'city',
      ]"
      :visibility="{ whois: false, ports: false }"
    />
    <FindingsModal
      v-if="selectedHost"
      title="Geolocation"
      :description="selectedHost.country"
      :open="locationModalOpen"
      @open="(open) => (locationModalOpen = open)"
    >
      <FindingsMetricsLocations :hosts="[selectedHost]" />
    </FindingsModal>
  </div>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudTableColumn } from "~/types/crud";
import { hostOS } from "~/constants";
import type { Host } from "~/types/models";

const route = useRoute();
const table = useTable();
const locationModalOpen = ref(false);
const selectedHost = ref();
const columns: CrudTableColumn<Host>[] = [
  {
    accessorKey: "ip",
    header: "IP",
    icon: "i-lucide-server",
    cell: ({ row }) => table.valueCell(row.getValue("ip")),
  },
  {
    accessorKey: "domain",
    header: "Domain",
    icon: "i-lucide-globe",
    cell: ({ row }) => table.valueCell(row.getValue("domain")),
  },
  {
    accessorKey: "os",
    header: "OS",
    icon: "i-lucide-monitor",
    cell: ({ row }) => {
      const osConfig = hostOS.find((o) => o.value === row.original.os_type);
      return table.iconAndValueCell(
        row.original.os,
        osConfig?.icon,
        osConfig?.color,
      );
    },
  },
  {
    accessorKey: "country",
    header: "Country",
    icon: "i-lucide-earth",
    cell: ({ row }) =>
      table.iconAndValueCell(
        row.getValue("country"),
        row.getValue("country")
          ? `cif:${(row.getValue("country") as string).toLowerCase()}`
          : "i-lucide-map-pin",
      ),
  },
  // todo: modal with the specific location when the latitude and the longitude exist
  {
    accessorKey: "city",
    header: "City",
    icon: "i-lucide-map-pin",
    cell: ({ row }) => {
      return row.original.latitude && row.original.longitude
        ? h(resolveComponent("UButton"), {
            label: row.original.city,
            color: "neutral",
            variant: "ghost",
            onClick: () => {
              selectedHost.value = row.original;
              locationModalOpen.value = true;
            },
          })
        : table.valueCell(row.original.city);
    },
  },
  {
    accessorKey: "analysis",
    header: "Malware Analysis",
    icon: "i-lucide-search-code",
    cell: ({ row }) => {
      const m = row.original.malicious_analysis || 0;
      const s = row.original.suspicious_analysis || 0;
      const total = row.original.total_analysis as number | null | undefined;
      if (!total) return table.noDataCell;
      else if (m === 0 && s === 0)
        return table.iconAndValueCell(
          total.toString(),
          "i-lucide-shield-check",
          "success",
        );
      const clean = Math.max(0, total - m - s);
      return h("div", { class: "flex flex-col gap-1 min-w-[4.5rem]" }, [
        h(
          "div",
          {
            class:
              "flex w-full h-1.5 rounded-full overflow-hidden bg-neutral-200 dark:bg-neutral-700",
          },
          [
            m > 0
              ? h("div", { style: `flex: ${m}`, class: "h-full bg-red-500" })
              : null,
            s > 0
              ? h("div", { style: `flex: ${s}`, class: "h-full bg-amber-400" })
              : null,
            clean > 0
              ? h("div", { style: `flex: ${clean}`, class: "h-full" })
              : null,
          ].filter(Boolean),
        ),
        h(
          "div",
          { class: "flex items-center gap-1" },
          [
            m > 0
              ? h(
                  resolveComponent("UTooltip"),
                  { text: "Malicious" },
                  {
                    default: () =>
                      table.badgeCell(m.toString(), undefined, "error"),
                  },
                )
              : null,
            s > 0
              ? h(
                  resolveComponent("UTooltip"),
                  { text: "Suspicious" },
                  {
                    default: () =>
                      table.badgeCell(s.toString(), undefined, "warning"),
                  },
                )
              : null,
            table.valueCell(`/ ${total}`),
          ].filter(Boolean),
        ),
      ]);
    },
  },
  {
    accessorKey: "reputation",
    header: "Reputation",
    icon: "i-lucide-badge-check",
    cell: ({ row }) => {
      const rep = row.original.reputation || 0;
      return table.iconAndValueCell(
        rep.toString(),
        rep > 0
          ? "i-lucide-badge-check"
          : rep < 0
            ? "i-lucide-badge-alert"
            : "i-lucide-badge-question-mark",
        rep > 0 ? "success" : rep < 0 ? "error" : "neutral",
      );
    },
  },
  {
    accessorKey: "whois",
    header: "Whois",
    icon: "i-lucide-database-search",
    cell: ({ row }) =>
      row.original.whois
        ? h(
            resolveComponent("UPopover"),
            {},
            {
              default: () =>
                h(resolveComponent("UButton"), {
                  icon: "i-lucide-info",
                  label: "WHOIS",
                  variant: "ghost",
                  color: "neutral",
                  size: "xs",
                }),
              content: () =>
                h(
                  "pre",
                  {
                    class:
                      "text-xs p-3 max-h-64 overflow-y-auto whitespace-pre-wrap max-w-xs font-mono",
                  },
                  row.original.whois,
                ),
            },
          )
        : table.noDataCell,
  },
  {
    accessorKey: "ports",
    header: "Ports",
    icon: "i-lucide-ethernet-port",
    cell: ({ row }) => {
      const basePath = `/ports?host=${row.original.id}`;
      return table.counterCell(
        row.original?.port?.length,
        route.params.project_id
          ? `/projects/${route.params.project_id}${basePath}`
          : basePath,
      );
    },
  },
];
</script>
