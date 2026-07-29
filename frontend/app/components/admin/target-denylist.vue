<template>
  <CrudPage disable-url-sync :config="config" />
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import * as z from "zod";
import { useUserStore } from "~/store/user";
import type { TargetDenylist } from "~/types/models";

const userStore = useUserStore();
const validation = useValidation();
const table = useTable();

const config: CrudConfig<TargetDenylist> = reactive({
  endpoint: "/api/target-denylist/",
  entityName: "Target Denylist",
  entityNamePlural: "Target Denylist",
  icon: "i-lucide-circle-off",
  tableColumns: [
    {
      accessorKey: "id",
      header: "ID",
      icon: "i-lucide-hash",
      cell: ({ row }) => table.valueCell(row.getValue("id")),
    },
    {
      accessorKey: "target",
      header: "Target",
      icon: "i-lucide-locate-fixed",
      cell: ({ row }) => table.valueCell(row.getValue("target"), "font-mono"),
    },
    {
      accessorKey: "blocked",
      header: "Blocked",
      icon: "i-lucide-ban",
      cell: ({ row }) => table.valueCell(row.getValue("blocked")),
    },
    {
      accessorKey: "default",
      header: "Default",
      cell: ({ row }) => {
        const isDefault = row.getValue("default");
        return h(
          "span",
          { class: isDefault ? "text-gray-600 font-medium" : "text-green-500" },
          isDefault ? "Yes" : "No",
        );
      },
    },
  ],
  tableColumnsVisibility: {
    id: false,
  },
  tableCopyId: false,
  searchable: true,
  searchPlaceholder: "Search denied targets...",
  filters: [],
  ordering: ["id", "target", "default", "blocked"],
  defaultOrdering: "-blocked,-id",
  pageSize: 5,
  pageSizeOptions: [5, 25, 50, 100],
  formFields: [
    {
      key: "target",
      label: "Target",
      type: "text",
      required: true,
      placeholder: "Enter target pattern (IP, domain, URL)",
    },
  ],
  formSchema: z.object({
    target: validation.target_regex("target", true, 100),
  }),
  deleteMessage: (item: TargetDenylist) =>
    buildDeleteMessage(
      "denied target pattern",
      item.target,
      undefined,
      "Targets matching this denied pattern could be created after the deletion",
    ),
  canRead: userStore.is_admin,
  canEdit: (item: TargetDenylist) => userStore.is_admin && !item.default,
  canDelete: (item: TargetDenylist) => userStore.is_admin && !item.default,
  canCreate: userStore.is_admin,
  showAccessDeniedError: false,
});
</script>
