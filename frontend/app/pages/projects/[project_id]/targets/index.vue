<template>
  <div>
    <CrudPage :config="config">
      <template v-if="userStore.is_auditor" #actions="{ item }">
        <TasksButton
          :project="{ id: parseInt(route.params.project_id) }"
          :target="item"
        />
      </template>
    </CrudPage>
    <ReportsButton
      v-model:open="showReportModal"
      :target-id="selectedTargetForReport?.id"
      :show="false"
    />
  </div>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, CrudTableColumn } from "~/types/crud";
import { useUserStore } from "~/store/user";
import type { Target } from "~/types/models";

const userStore = useUserStore();
const route = useRoute();
const backend = useBackend();
const selectedTargetForReport = ref<Target | null>(null);
const showReportModal = ref(false);

function createTargetLink(targetId: string, count: number, path: string) {
  if (count === 0) {
    return h("span", { class: "font-medium text-muted-foreground" }, "0");
  }
  const linkPath = `/projects/${route.params.project_id}/${path}`;
  const queryParam = `target=${targetId}`;
  const href = `${linkPath}?${queryParam}`;
  return h(
    "a",
    {
      href,
      class: "font-medium text-primary hover:underline",
    },
    count.toString(),
  );
}
// todo: add link to DefectDojo if sync is enabled
const config: CrudConfig<Target> = reactive({
  endpoint: "/api/targets/",
  entityName: "Target",
  entityNamePlural: "Targets",
  icon: "i-lucide-locate-fixed",
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
        h("span", { class: "font-medium" }, row.getValue("target")),
    },
    {
      accessorKey: "type",
      header: "Type",
      icon: "i-lucide-tag",
      cell: ({ row }) => {
        const type = row.getValue("type") as string;
        const typeConfig = backend.targetTypes.find((t) => t.value === type);
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
                name: typeConfig?.icon || "i-lucide-locate-fixed",
                class: "w-3 h-3 mr-1",
              }),
              type,
            ],
          },
        );
      },
    },
    {
      accessorKey: "target_ports",
      header: "Target Ports",
      icon: "i-lucide-server",
      cell: ({ row }) => {
        const targetPorts = row.getValue(
          "target_ports",
        ) as Target["target_ports"];
        const count = targetPorts?.length || 0;
        return h("span", { class: "font-medium" }, count.toString());
      },
    },
    {
      accessorKey: "tasks",
      header: "Scans",
      icon: "i-lucide-play",
      cell: ({ row }) => {
        const tasks = row.getValue("tasks") as Target["tasks"];
        const count = tasks?.length || 0;
        const targetId = (row.original as Target).id;
        return createTargetLink(targetId.toString(), count, "scans");
      },
    },
    {
      accessorKey: "notes",
      header: "Notes",
      icon: "i-lucide-notebook",
      cell: ({ row }) => {
        const notes = row.getValue("notes") as Target["notes"];
        const count = notes?.length || 0;
        const targetId = (row.original as Target).id;
        return createTargetLink(targetId.toString(), count, "notes");
      },
    },
    {
      accessorKey: "reports",
      header: "Reports",
      icon: "i-lucide-file-text",
      cell: ({ row }) => {
        const reports = row.getValue("reports") as Target["reports"];
        const count = reports?.length || 0;
        const targetId = (row.original as Target).id;
        return createTargetLink(targetId.toString(), count, "reports");
      },
    },
  ] as CrudTableColumn<Target>[],
  tableColumnsVisibility: {
    id: false,
    notes: false,
    reports: false,
  },
  itemLink: (target: Target) =>
    `/projects/${route.params.project_id}/targets/${target.id}`,
  searchable: true,
  searchPlaceholder: "Search targets...",
  filters: [
    {
      key: "type",
      label: "Type",
      icon: "i-lucide-tag",
      type: "select" as const,
      options: backend.targetTypes,
      labelKey: "value",
    },
  ],
  defaultFilters: { project: route.params.project_id },
  ordering: ["id", "target", "type"],
  defaultOrdering: "id",
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
  defaultBody: { project: route.params.project_id },
  createForm: resolveComponent("FormTarget"),
  onCreation: (data: Record<string, unknown>) => {
    if (Array.isArray(data.targets) && data.targets.length === 1) {
      navigateTo(
        `/projects/${route.params.project_id}/targets/${data.targets[0].id}`,
      );
    }
  },
  deleteMessage: (target: Target) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this target?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: target.target,
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "error",
        icon: "i-lucide-triangle-alert",
        title: "Permanent deletion",
        description:
          "All associated data including assets, findings, and scans will be permanently deleted. This action cannot be undone.",
        class: "mt-4",
      },
    },
  ],
  canRead: true,
  canEdit: false,
  canCreate: userStore.is_auditor,
  canDelete: userStore.is_auditor,
  // todo: add custom action to take notes on target
  customDropdownActions: (target: Target) => {
    return target.tasks && target.tasks.length > 0 && userStore.is_auditor
      ? [
          {
            label: "Generate a report",
            icon: "i-lucide-file-text",
            color: "info",
            onSelect: (target: Target) => {
              selectedTargetForReport.value = target;
              showReportModal.value = true;
            },
          },
        ]
      : [];
  },
});
</script>
