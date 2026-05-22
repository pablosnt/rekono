<template>
  <CrudPage disable-url-sync :config="config">
    <template #before>
      <UAlert
        v-if="!target"
        color="neutral"
        variant="subtle"
        icon="i-lucide-info"
        :description="
          user
            ? 'Your HTTP headers can be overridden per target'
            : 'These HTTP headers can be customized per user or target'
        "
        class="mb-2"
      />
      <UAlert
        color="warning"
        variant="subtle"
        icon="i-lucide-shield"
        description="Don't add sensitive information in HTTP headers. Credetials must be configured on each target authentication"
        class="mb-4"
      />
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import * as z from "zod";

const props = defineProps<{
  user?: number;
  target?: number;
  canRead: boolean;
  canCreate: boolean;
  canEdit: boolean;
  canDelete: boolean;
  showAccessDeniedError?: boolean;
}>();

const table = useTable();
const validation = useValidation();

let defaultBody = {};
let defaultFilters = {};
if (props.target) {
  defaultBody = { target: props.target };
  defaultFilters = { user__isnull: true, target: props.target };
} else if (props.user) {
  defaultBody = { user: props.user };
  defaultFilters = { user: props.user, target__isnull: true };
} else {
  defaultFilters = { user__isnull: true, target__isnull: true };
}

const config: CrudConfig = reactive({
  endpoint: "/api/http-headers/",
  entityName: "HTTP Header",
  entityNamePlural: "HTTP Headers",
  icon: "i-lucide-globe",
  tableColumns: [
    {
      accessorKey: "id",
      header: "ID",
      icon: "i-lucide-hash",
      cell: ({ row }) => table.valueCell(row.getValue("id")),
    },
    {
      accessorKey: "key",
      header: "Header",
      icon: "i-lucide-case-sensitive",
      cell: ({ row }) => table.valueCell(row.getValue("key")),
    },
    {
      accessorKey: "value",
      header: "Value",
      icon: "i-lucide-text-cursor-input",
      cell: ({ row }) =>
        table.valueCell(row.getValue("value"), "text-muted-foreground"),
    },
  ],
  tableColumnsVisibility: {
    id: false,
  },
  tableCopyId: false,
  searchable: true,
  searchPlaceholder: "Search HTTP headers...",
  filters: [],
  ordering: ["id", "key", "value"],
  defaultOrdering: "id",
  defaultBody,
  defaultFilters,
  formFields: [
    {
      key: "key",
      label: "Header",
      type: "text",
      required: true,
      placeholder: "Content-Type",
    },
    {
      key: "value",
      label: "Value",
      type: "text",
      required: true,
      placeholder: "application/json",
    },
  ],
  formSchema: z.object({
    key: validation.name("key", true, 100),
    value: z
      .string("Value is required")
      .min(1)
      .max(500)
      .refine((value) => /^[^;<>]*$/u.test(value), {
        message: "Invalid value",
      }),
  }),
  canRead: props.canRead,
  canCreate: props.canCreate,
  canEdit: props.canEdit,
  canDelete: props.canDelete,
  showAccessDeniedError: props.showAccessDeniedError,
});
</script>
