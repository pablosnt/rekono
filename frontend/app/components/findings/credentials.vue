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
import { h } from "vue";
import type { CrudTableColumn } from "~/types/crud";
import { hostOS } from "~/constants";

const columns: CrudTableColumn<Record<string, unknown>>[] = [
  {
    accessorKey: "host",
    header: "Host",
    icon: "i-lucide-server",
    cell: ({ row }) => {
      const finding = row.original;
      if (finding.technology?.port?.host) {
        const config = hostOS.find((c) => c.value === finding.host?.os_type);
        return h(
          "a",
          {
            href: `/projects/${finding.project}/hosts/${finding.technology?.port?.host.id}`,
            class:
              "flex items-center gap-2 font-medium hover:text-primary hover:underline",
            onClick: (e: Event) => e.stopPropagation(),
          },
          [
            h(resolveComponent("UIcon"), {
              name: config?.icon || "i-lucide-server",
              class: `text-lg text-${config?.color || "neutral"}`,
            }),
            finding.technology?.port?.host.ip ||
              finding.technology?.port?.host.domain,
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
      return finding.technology?.port
        ? h(
            "a",
            {
              href: `/projects/${finding.project}/ports/${finding.technology?.port.id}`,
              class:
                "flex items-center gap-2 hover:text-primary hover:underline",
              onClick: (e: Event) => e.stopPropagation(),
            },
            [
              h(resolveComponent("UIcon"), {
                name: getPortIcon(
                  finding.technology?.port.port,
                  finding.technology?.port.service,
                ),
                class: "text-2xl",
              }),
              finding.technology?.port.port,
            ],
          )
        : h("span", { class: "text-sm" }, "—");
    },
  },
  {
    accessorKey: "technology",
    header: "Technology",
    icon: "i-lucide-layers",
    cell: ({ row }) => {
      const finding = row.original;
      return finding.technology
        ? h(
            "a",
            {
              href: `/projects/${finding.project}/technologies/${finding.technology.id}`,
              class: "font-medium hover:text-primary hover:underline",
              onClick: (e: Event) => e.stopPropagation(),
            },
            [`${finding.technology?.name} - ${finding.technology?.version}`],
          )
        : h("span", { class: "text-sm" }, "—");
    },
  },
  {
    accessorKey: "email",
    header: "Mail",
    icon: "i-lucide-mail",
    cell: ({ row }) => {
      const value = row.getValue("email") as string;
      return h("span", { class: "text-sm" }, value ? value : "—");
    },
  },
  {
    accessorKey: "username",
    header: "Username",
    icon: "i-lucide-user",
    cell: ({ row }) => {
      const value = row.getValue("username") as string;
      return h("span", { class: "text-sm" }, value ? value : "—");
    },
  },
  {
    accessorKey: "secret",
    header: "Secret",
    icon: "i-lucide-key",
    cell: ({ row }) => {
      const value = row.getValue("secret") as string;
      return h("span", { class: "text-sm" }, value ? value : "—");
    },
  },
  {
    accessorKey: "context",
    header: "Context",
    icon: "i-lucide-message-circle-code",
    cell: ({ row }) => {
      const value = row.getValue("context") as string;
      return h("span", { class: "text-sm" }, value ? value : "—");
    },
  },
];
</script>
