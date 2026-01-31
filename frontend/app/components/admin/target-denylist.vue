<template>
  <CrudPage :config="config" />
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig } from "~/types/crud";
import * as z from "zod";
import { useUserStore } from "~/store/user";
import type { TargetDenylist } from "~/types/target-denylist";

const userStore = useUserStore();
const validation = useValidation();

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
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("id")),
    },
    {
      accessorKey: "target",
      header: "Target",
      icon: "i-lucide-locate-fixed",
      cell: ({ row }) =>
        h("span", { class: "font-medium font-mono" }, row.getValue("target")),
    },
    {
      accessorKey: "default",
      header: "Default",
      cell: ({ row }) => {
        const isDefault = row.getValue("default");
        return h(
          "span",
          {
            class: isDefault ? "text-gray-600 font-medium" : "text-green-500",
          },
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
  ordering: ["id", "target", "default"],
  defaultOrdering: "-id",
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
  deleteMessage: (item: TargetDenylist) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this denied target pattern?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: item.target,
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "warning",
        icon: "i-lucide-triangle-alert",
        description:
          "Targets matching this denied pattern could be created after the deletion",
        class: "mt-4",
      },
    },
  ],
  canRead: userStore.is_admin,
  canEdit: (item: TargetDenylist) => userStore.is_admin && !item.default,
  canDelete: (item: TargetDenylist) => userStore.is_admin && !item.default,
  canCreate: userStore.is_admin,
  showAccessDeniedError: false,
});
</script>
