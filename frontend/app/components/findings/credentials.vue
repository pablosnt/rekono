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

const route = useRoute();
const backend = useBackend();
const columns: CrudTableColumn<Record<string, unknown>>[] = [
  {
    accessorKey: "host",
    header: "Host",
    icon: "i-lucide-server",
    cell: ({ row }) => {
      const finding = row.original;
      return finding.technology?.port?.host
        ? h(
            "a",
            {
              href: route.params.project_id
                ? `/projects/${route.params.project_id}/hosts/${finding.technology?.port?.host.id}`
                : `/hosts/${finding.technology?.port?.host.id}`,
              target: "_blank",
              rel: "noopener noreferrer",
              class:
                "flex items-center gap-2 font-medium hover:text-primary hover:underline",
              onClick: (e: Event) => e.stopPropagation(),
            },
            [
              // TODO: Icon per host OS
              h(resolveComponent("UIcon"), {
                name: "i-lucide-server",
                class: "text-lg",
              }),
              finding.technology?.port?.host.ip ||
                finding.technology?.port?.host.domain,
            ],
          )
        : h("span", { class: "text-sm" }, "—");
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
              href: route.params.project_id
                ? `/projects/${route.params.project_id}/ports/${finding.technology?.port.id}`
                : `/ports/${finding.technology?.port.id}`,
              target: "_blank",
              rel: "noopener noreferrer",
              class:
                "flex items-center gap-2 font-medium hover:text-primary hover:underline",
              onClick: (e: Event) => e.stopPropagation(),
            },
            [
              h(resolveComponent("UIcon"), {
                name: backend.getPortIcon(
                  finding.technology?.port.port,
                  finding.technology?.port.service,
                ),
                class: "text-lg",
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
              href: route.params.project_id
                ? `/projects/${route.params.project_id}/technologies/${finding.technology.id}`
                : `/technologies/${finding.technology.id}`,
              target: "_blank",
              rel: "noopener noreferrer",
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
