<template>
  <CrudPage disable-url-sync :config="apiTokensConfig" />
</template>

<script setup lang="ts">
import * as z from "zod";
import { today, getLocalTimeZone } from "@internationalized/date";
import type { CrudTableColumn } from "~/types/crud";
import type { ApiToken } from "~/types/models";

const validation = useValidation();
const table = useTable();

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
      cell: ({ row }) => table.valueCell(row.getValue("name")),
    },
    {
      accessorKey: "expiration",
      header: "Expiration",
      icon: "i-lucide-calendar",
      cell: ({ row }) => {
        const expiration = row.getValue("expiration") as string;
        return table.valueCell(
          expiration ? new Date(expiration).toDateString() : undefined,
        );
      },
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
      initialCalendarDate: today(getLocalTimeZone()).add({ months: 6 }),
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
  createForm: markRaw(resolveComponent("ApiTokensForm")),
  updateOnCreateModalOpen: true,
  deleteMessage: (token: ApiToken) =>
    buildDeleteMessage("API token", token.name),
  emptyMessage: "You don't have any API token yet",
  canRead: true,
  canEdit: false,
  canDelete: true,
  canCreate: true,
  showAccessDeniedError: false,
});
</script>
