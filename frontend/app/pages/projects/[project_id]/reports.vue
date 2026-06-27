<template>
  <CrudPage :config="config">
    <template #actions="{ item }">
      <UTooltip v-if="item.status === 'Ready'" text="Download">
        <UButton
          icon="i-lucide-download"
          variant="ghost"
          size="xl"
          aria-label="Download report"
          @click="api.download(`/api/reports/${item.id}/download/`)"
        />
      </UTooltip>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import type { CrudConfig, CrudTableColumn, FilterOption } from "~/types/crud";
import type { Report } from "~/types/models";
import { reportFormats, reportStatuses } from "~/constants";

const options = useOptions();
const api = useApi();
const route = useRoute();
const table = useTable();
const userOptions = ref<FilterOption[]>([]);

onMounted(() => {
  options.users(userOptions, { is_active: true });
});

const config: CrudConfig<Report> = reactive({
  endpoint: "/api/reports/",
  entityName: "Report",
  entityNamePlural: "Reports",
  icon: "i-lucide-file-text",
  tableColumns: [
    {
      accessorKey: "id",
      header: "ID",
      icon: "i-lucide-hash",
      cell: ({ row }) => table.valueCell(row.getValue("id")),
    },
    {
      accessorKey: "source",
      header: "Source",
      icon: "i-lucide-link",
      cell: ({ row }) => {
        if (row.original.task) {
          return table.linkCell(
            `/projects/${route.params.project_id}/scans/${row.original.task.id}`,
            "i-lucide-play",
            undefined,
            getTaskName(row.original.task, true),
          );
        } else if (row.original.target) {
          return table.linkCell(
            `/projects/${route.params.project_id}/targets/${row.original.target.id}`,
            "i-lucide-locate-fixed",
            undefined,
            row.original.target.target,
          );
        }
        return table.iconAndValueCell("i-lucide-folder", "Full project");
      },
    },
    {
      accessorKey: "status",
      header: "Status",
      icon: "i-lucide-activity",
      cell: ({ row }) => {
        const status = row.getValue("status") as string;
        const statusConfig = reportStatuses.find((s) => s.value === status);
        return table.badgeCell(
          statusConfig?.label || status,
          statusConfig?.icon || "i-lucide-circle",
          statusConfig?.color || "neutral",
        );
      },
    },
    {
      accessorKey: "format",
      header: "Format",
      icon: "i-lucide-file-type",
      cell: ({ row }) => {
        const format = row.getValue("format") as string;
        const formatConfig = reportFormats.find((f) => f.value === format);
        return table.badgeCell(
          format.toUpperCase(),
          formatConfig?.icon || "i-lucide-file",
        );
      },
    },
    {
      accessorKey: "user",
      header: "User",
      icon: "i-lucide-user",
      cell: ({ row }) => table.usernameCell(row.getValue("user")),
    },
    {
      accessorKey: "date",
      header: "Date",
      icon: "i-lucide-calendar",
      cell: ({ row }) =>
        table.valueCell(new Date(row.getValue("date")).toLocaleDateString()),
    },
  ] as CrudTableColumn<Report>[],
  tableColumnsVisibility: {
    id: false,
    user: false,
  },
  searchable: true,
  searchPlaceholder: "Search reports...",
  acceptedFilters: [
    {
      key: "task",
      label: "Task",
      icon: "i-lucide-play",
      loadOption: (value) => options.task(value),
    },
    {
      key: "target",
      label: "Target",
      icon: "i-lucide-locate-fixed",
      loadOption: (value) => options.target(value),
    },
  ],
  filters: [
    {
      key: "report_format",
      label: "Format",
      icon: "i-lucide-file-type",
      type: "select" as const,
      options: reportFormats,
    },
    {
      key: "status",
      label: "Status",
      icon: "i-lucide-activity",
      type: "select" as const,
      labelKey: "value",
      options: reportStatuses,
    },
    {
      key: "user",
      label: "User",
      icon: "i-lucide-user",
      type: "select" as const,
      options: userOptions,
    },
  ],
  defaultFilters: { project: route.params.project_id },
  ordering: ["id", "target", "task", "status", "format", "user", "date"],
  defaultOrdering: "-id",
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
  defaultBody: { project: route.params.project_id },
  createForm: resolveComponent("ReportsForm"),
  deleteMessage: (report: Report) =>
    buildDeleteMessage(
      "report",
      `${report.format.toUpperCase()} report with findings from ${report.task ? getTaskName(report.task, true) : report.target ? report.target.target : "full project"}`,
    ),
  canRead: true,
  canCreate: true,
  canEdit: false,
  canDelete: true,
});
</script>
