<template>
  <div>
    <FindingsMultiple
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
      is-asset
    />
    <UModal
      v-if="selectedHost"
      v-model:open="locationModalOpen"
      title="Geolocation"
      :description="
        selectedHost.city ? selectedHost.city : selectedHost.country
      "
      :ui="{ content: 'sm:max-w-3xl sm:max-h-xl' }"
    >
      <template v-if="selectedHost.country && selectedHost.city" #description>
        <div class="flex items-center gap-2">
          <UIcon :name="`cif:${selectedHost.country.toLowerCase()}`" />
          <span class="text-base">{{ selectedHost.city }}</span>
        </div>
      </template>
      <template #body>
        <FindingsHostsLocations :hosts="[selectedHost]" />
      </template>
    </UModal>
    <UModal
      v-if="selectedHost"
      v-model:open="malwareModalOpen"
      title="Malware Analysis"
      :ui="{ content: 'sm:max-w-3xl sm:max-h-xl' }"
    >
      <template #body>
        <FindingsHostsMalware :host="selectedHost" />
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { h } from "vue";
import { hostOS } from "~/constants";
import { useIntegrationsStore } from "~/store/integrations";

const route = useRoute();
const table = useTable();
const integrations = useIntegrationsStore();
const locationModalOpen = ref(false);
const malwareModalOpen = ref(false);
const selectedHost = ref();

const columns = computed(() => [
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
      row.original.country
        ? row.original.latitude && row.original.longitude
          ? h(resolveComponent("UButton"), {
              label: row.original.country,
              icon: `cif:${row.original.country.toLowerCase()}`,
              color: "neutral",
              variant: "ghost",
              onClick: () => {
                selectedHost.value = row.original;
                locationModalOpen.value = true;
              },
            })
          : table.iconAndValueCell(
              row.original.country,
              `cif:${row.original.country.toLowerCase()}`,
            )
        : table.noDataCell,
  },
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
  ...(integrations.virustotal.integration?.enabled
    ? [
        {
          accessorKey: "analysis",
          header: "Malware Analysis",
          icon: "i-lucide-search-code",
          cell: ({ row }) => {
            if ((row.original.total_analysis ?? 0) > 0) {
              const percentage =
                (Math.max(
                  0,
                  (row.original.total_analysis ?? 0) -
                    (row.original.malicious_analysis ?? 0) -
                    (row.original.suspicious_analysis ?? 0),
                ) *
                  100) /
                row.original.total_analysis;
              return h(resolveComponent("UButton"), {
                label: `${percentage.toPrecision(3)}% Legitimate`,
                color:
                  percentage > 50
                    ? "success"
                    : percentage < 20
                      ? "error"
                      : "warning",
                variant: "subtle",
                onClick: () => {
                  selectedHost.value = row.original;
                  malwareModalOpen.value = true;
                },
              });
            }
            return table.noDataCell;
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
      ]
    : []),
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
]);

onMounted(integrations.fetchVirusTotal);
</script>
