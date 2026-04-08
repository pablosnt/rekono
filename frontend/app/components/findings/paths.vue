<template>
  <Findings
    endpoint="/api/paths/"
    entity-name="Path"
    entity-name-plural="Paths"
    icon="i-lucide-slash"
    :columns="columns"
    :filters="[
      {
        key: 'type',
        label: 'Type',
        icon: 'i-lucide-tag',
        type: 'select',
        options: pathTypes as FilterOption[],
        labelKey: 'value',
      },
    ]"
    :ordering="['id', 'port', ('port__host', 'Host'), 'path', 'status', 'type']"
  />
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudTableColumn, FilterOption } from "~/types/crud";
import { hostOS, pathTypes } from "~/constants";

const columns: CrudTableColumn<Record<string, unknown>>[] = [
  {
    accessorKey: "host",
    header: "Host",
    icon: "i-lucide-server",
    cell: ({ row }) => {
      const finding = row.original;
      if (finding.port?.host) {
        const config = hostOS.find(
          (c) => c.value === finding.port?.host?.os_type,
        );
        return h(
          "a",
          {
            href: `/projects/${finding.project}/hosts/${finding.port?.host.id}`,
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
            finding.port?.host.ip || finding.port?.host.domain,
          ],
        );
      } else {
        return h("span", { class: "text-sm" }, "—");
      }
    },
  },
  {
    accessorKey: "Port",
    header: "Port",
    icon: "i-lucide-ethernet-port",
    cell: ({ row }) => {
      const finding = row.original;
      return finding.port
        ? h(
            "a",
            {
              href: `/projects/${finding.project}/ports/${finding.port.id}`,
              class:
                "flex items-center gap-2 font-medium hover:text-primary hover:underline",
              onClick: (e: Event) => e.stopPropagation(),
            },
            [
              // TODO: This kind of cell should be a component. We are duplicating a lot of HTML code, as TS
              h(resolveComponent("UIcon"), {
                name: getPortIcon(finding.port.port, finding.port.service),
                class: "text-2xl",
              }),
              finding.port.port,
            ],
          )
        : h("span", { class: "text-sm" }, "—");
    },
  },
  {
    accessorKey: "path",
    header: "Path",
    icon: "i-lucide-slash",
    cell: ({ row }) => {
      return h("span", { class: "font-mono text-sm" }, row.getValue("path"));
    },
  },
  {
    accessorKey: "type",
    header: "Type",
    icon: "i-lucide-tag",
    cell: ({ row }) => {
      const type = row.getValue("type") as string;
      if (!type) return h("span", { class: "text-sm" }, "—");
      const config = pathTypes.find((t) => t.value === type);
      return h(
        resolveComponent("UBadge"),
        { color: "neutral", variant: "subtle" },
        {
          default: () => [
            h(resolveComponent("UIcon"), {
              name: config?.icon || "i-lucide-slash",
              class: "mr-1 text-lg",
            }),
            type,
          ],
        },
      );
    },
  },
  {
    accessorKey: "httpStatus",
    header: "HTTP Status",
    icon: "i-lucide-hash",
    cell: ({ row }) => {
      const status = row.getValue("status") as number | null;
      if (!status) return h("span", { class: "text-sm" }, "—");
      return h(
        resolveComponent("UBadge"),
        { color: httpStatusColor(status), variant: "subtle" },
        { default: () => String(status) },
      );
    },
  },
  {
    accessorKey: "information",
    header: "Information",
    icon: "i-lucide-info",
    cell: ({ row }) => {
      return h("span", { class: "text-sm" }, row.getValue("extra_info") || "—");
    },
  },
];
</script>
