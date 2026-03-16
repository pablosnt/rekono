<template>
  <CrudPage :config="apiTokensConfig" />
</template>

<script setup lang="ts">
import * as z from "zod";
import { h, resolveComponent } from "vue";
import { today, getLocalTimeZone } from "@internationalized/date";
import type { CrudTableColumn } from "~/types/crud";
import type { ApiToken } from "~/types/models";

const validation = useValidation();

const apiTokensConfig = ref({
  endpoint: "/api/api-tokens/",
  entityName: "API token",
  entityNamePlural: "API tokens",
  icon: "i-lucide-code-xml",
  tableColumns: [
    {
      accessorKey: "name",
      header: "Name",
      icon: "i-lucide-key",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("name")),
    },
    {
      accessorKey: "expiration",
      header: "Expiration",
      icon: "i-lucide-calendar",
      cell: ({ row }) =>
        h(
          "span",
          { class: "font-medium" },
          new Date(row.getValue("expiration")).toDateString(),
        ),
    },
  ] as CrudTableColumn<ApiToken>[],
  tableCopyId: false,
  ordering: ["id", "name", "expiration"],
  defaultOrdering: "-id",
  pageSize: 5,
  pageSizeOptions: [5, 25, 50, 100],
  formFields: [
    {
      key: "name",
      label: "Name",
      type: "text",
      placeholder: "Enter token name",
      required: true,
      size: "xl",
      icon: "i-lucide-key",
    },
    {
      key: "expiration",
      label: "Expiration",
      type: "date",
      required: false,
      size: "xl",
      icon: "i-lucide-calendar",
      minValue: today(getLocalTimeZone()).add({ days: 1 }),
    },
  ],
  formSchema: z.object({
    name: validation.name("Token name"),
    expiration: z
      .any()
      .optional()
      .refine((value) => value > today(getLocalTimeZone()), {
        message: `Invalid expiration date`,
      }),
  }),
  createForm: resolveComponent("ApiTokensForm"),
  updateOnCreateModalOpen: true,
  deleteMessage: (token: ApiToken) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this API token?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: token.name,
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
  ],
  emptyMessage: "You don't have any API token yet",
  canRead: true,
  canEdit: false,
  canDelete: true,
  canCreate: true,
  showAccessDeniedError: false,
});
</script>
