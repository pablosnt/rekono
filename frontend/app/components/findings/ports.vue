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
        options: backend.portStatuses,
        labelKey: 'value',
      },
      {
        key: 'protocol',
        label: 'Protocol',
        icon: 'i-lucide-network',
        type: 'select',
        options: backend.portProtocols,
      },
    ]"
    :ordering="['id', 'host', 'port', 'status', 'protocol', 'service']"
  />
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudTableColumn } from "~/types/crud";

const backend = useBackend();

const columns: CrudTableColumn<Record<string, unknown>>[] = [
  {
    accessorKey: "host",
    header: "Host",
    icon: "i-lucide-server",
    cell: ({ row }) => {
      const finding = row.original;
      if (finding.host) {
        const config = backend.hostOS.find(
          (c) => c.value === finding.host?.os_type,
        );
        return h(
          "a",
          {
            href: `/projects/${finding.project}/hosts/${finding.host.id}`,
            target: "_blank",
            rel: "noopener noreferrer",
            class:
              "flex items-center gap-2 font-medium hover:text-primary hover:underline",
            onClick: (e: Event) => e.stopPropagation(),
          },
          [
            h(resolveComponent("UIcon"), {
              name: config?.icon || "i-lucide-server",
              color: config?.color || "neutral",
              class: "text-lg",
            }),
            finding.host.ip || finding.host.domain,
          ],
        );
      } else {
        return h("span", { class: "text-sm" }, "—");
      }
    },
  },
  {
    accessorKey: "port",
    header: "Port",
    icon: "i-lucide-ethernet-port",
    cell: ({ row }) => {
      const finding = row.original;
      return h("span", { class: "text-sm" }, String(finding.port));
    },
  },
  {
    accessorKey: "protocol",
    header: "Protocol",
    icon: "i-lucide-network",
    cell: ({ row }) => {
      const protocol = row.getValue("protocol") as string;
      if (!protocol) return h("span", { class: "text-sm" }, "—");
      return h(
        resolveComponent("UBadge"),
        { color: "neutral", variant: "subtle" },
        { default: () => protocol },
      );
    },
  },
  {
    accessorKey: "service",
    header: "Service",
    icon: "i-lucide-layers",
    cell: ({ row }) => {
      const finding = row.original;
      const service = finding.service as string | undefined;
      const port = finding.port as number;
      const icon = backend.getPortIcon(port, service);
      return h("span", { class: "flex items-center gap-2 text-sm" }, [
        h(resolveComponent("UIcon"), { name: icon, class: "text-lg shrink-0" }),
        service ? service : h("span", { class: "text-muted" }, "—"),
      ]);
    },
  },
  {
    accessorKey: "portStatus",
    header: "Port Status",
    icon: "i-lucide-chevrons-left-right-ellipsis",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      if (!status) return h("span", { class: "text-sm" }, "—");
      const config = backend.portStatuses.find((s) => s.value === status);
      return h(
        resolveComponent("UBadge"),
        {
          color: config?.color,
          variant: "subtle",
          class: "font-medium",
        },
        {
          default: () => [
            h(resolveComponent("UIcon"), {
              name: config?.icon,
              class: "mr-1 text-lg",
            }),
            status,
          ],
        },
      );
    },
  },
];
</script>
