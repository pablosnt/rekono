<template>
  <CrudPage :config="config">
    <template #actions="{ item }">
      <UTooltip v-if="item.status === 'Ready'" text="Download">
        <UButton
          icon="i-lucide-download"
          variant="ghost"
          size="xl"
          @click="api.download(`/api/reports/${item.id}/download/`)"
        />
      </UTooltip>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, CrudTableColumn, FilterOption } from "~/types/crud";
import type { Report } from "~/types/models";

definePageMeta({ layout: "project" });
const backend = useBackend();
const api = useApi();
const route = useRoute();
const userOptions = ref<FilterOption[]>([]);
const targetOptions = ref<FilterOption[]>([]);
const taskOptions = ref<FilterOption[]>([]);

onMounted(() => {
  backend.getUserOptions(userOptions, { is_active: true });
  backend.getTargetOptions(targetOptions, { project: route.params.project_id });
  backend.getTaskOptions(taskOptions, { project: route.params.project_id });
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
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("id")),
    },
    {
      accessorKey: "source",
      header: "Source",
      icon: "i-lucide-link",
      cell: ({ row }) => {
        const report = row.original as Report;
        if (report.task) {
          return h(
            "div",
            { class: "flex items-center gap-2 hover:text-primary" },
            [
              h(resolveComponent("UIcon"), {
                name: "i-lucide-play",
                class: "w-4 h-4 text-muted-foreground",
              }),
              h(
                "a",
                {
                  href: `/projects/${route.params.project_id}/scans/${report.task.id}`,
                  class: "hover:underline font-medium",
                },
                backend.getTaskName(report.task, true),
              ),
            ],
          );
        } else if (report.target) {
          return h(
            "div",
            { class: "flex items-center gap-2 hover:text-primary" },
            [
              h(resolveComponent("UIcon"), {
                name: "i-lucide-locate-fixed",
                class: "w-4 h-4 text-muted-foreground",
              }),
              h(
                "a",
                {
                  href: `/projects/${route.params.project_id}/targets/${report.target.id}`,
                  class: "hover:underline font-medium",
                },
                report.target.target,
              ),
            ],
          );
        }
        return h("div", { class: "flex items-center gap-2" }, [
          h(resolveComponent("UIcon"), {
            name: "i-lucide-folder",
            class: "w-4 h-4 text-muted-foreground",
          }),
          h("span", { class: "text-muted-foreground" }, "Full project"),
        ]);
      },
    },
    {
      accessorKey: "status",
      header: "Status",
      icon: "i-lucide-activity",
      cell: ({ row }) => {
        const status = row.getValue("status") as string;
        const statusConfig = backend.reportStatuses.find(
          (s) => s.value === status,
        );
        return h(
          resolveComponent("UBadge"),
          {
            color: statusConfig?.color || "neutral",
            variant: "subtle",
            class: "font-medium",
          },
          {
            default: () => [
              h(resolveComponent("UIcon"), {
                name: statusConfig?.icon || "i-lucide-circle",
                class: "mr-1 text-lg",
              }),
              statusConfig?.label || status,
            ],
          },
        );
      },
    },
    {
      accessorKey: "format",
      header: "Format",
      icon: "i-lucide-file-type",
      cell: ({ row }) => {
        const format = row.getValue("format") as string;
        const formatConfig = backend.reportFormats.find(
          (f) => f.value === format,
        );
        return h(
          resolveComponent("UBadge"),
          {
            color: "neutral",
            variant: "subtle",
            class: "font-medium",
          },
          {
            default: () => [
              h(resolveComponent("UIcon"), {
                name: formatConfig?.icon || "i-lucide-file",
                class: "mr-1 text-lg",
              }),
              format.toUpperCase(),
            ],
          },
        );
      },
    },
    {
      accessorKey: "user",
      header: "User",
      icon: "i-lucide-user",
      cell: ({ row }) => {
        const user = row.getValue("user") as Report["user"];
        return h(
          "span",
          { class: "font-medium" },
          user?.username ? `@${user.username}` : "—",
        );
      },
    },
    {
      accessorKey: "date",
      header: "Date",
      icon: "i-lucide-calendar",
      cell: ({ row }) => {
        const date = row.getValue("date") as string;
        return h(
          "span",
          { class: "font-medium" },
          new Date(date).toLocaleDateString(),
        );
      },
    },
  ] as CrudTableColumn<Report>[],
  tableColumnsVisibility: {
    id: false,
    user: false,
  },
  searchable: true,
  searchPlaceholder: "Search reports...",
  filters: [
    {
      key: "task",
      label: "Task",
      icon: "i-lucide-play",
      type: "select" as const,
      options: taskOptions,
    },
    {
      key: "target",
      label: "Target",
      icon: "i-lucide-locate-fixed",
      type: "select" as const,
      options: targetOptions,
      valueKey: "id",
      labelKey: "target",
    },
    {
      key: "report_format",
      label: "Format",
      icon: "i-lucide-file-type",
      type: "select" as const,
      options: backend.reportFormats,
    },
    {
      key: "status",
      label: "Status",
      icon: "i-lucide-activity",
      type: "select" as const,
      labelKey: "value",
      options: backend.reportStatuses,
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
  deleteMessage: (report: Report) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this report?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: `${report.format.toUpperCase()} report with findings from ${report.task ? backend.getTaskName(report.task, true) : report.target ? report.target.target : "full project"}`,
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
  ],
  canRead: true,
  canCreate: true,
  canEdit: false,
  canDelete: true,
});
</script>
