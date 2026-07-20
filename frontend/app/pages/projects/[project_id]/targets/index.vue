<template>
  <div>
    <CrudPage :config="config" @deleted="refreshPanelCounts()">
      <template v-if="userStore.is_auditor" #actions="{ item }">
        <TasksButton
          :project="{ id: parseInt(route.params.project_id) }"
          :target="item"
        />
      </template>
    </CrudPage>
    <ReportsButton
      v-model:open="showReportModal"
      :target-id="selectedTarget?.id"
      only-modal
    />
    <NotesButton
      v-if="selectedTarget"
      ref="notesButton"
      :target="selectedTarget?.id"
    />
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import { useUserStore } from "~/store/user";
import type { Target } from "~/types/models";
import { targetTypes } from "~/constants";
import { useIntegrationsStore } from "~/store/integrations";

const userStore = useUserStore();
const route = useRoute();
const table = useTable();
const integrations = useIntegrationsStore();
const { showDefectDojo } = useCurrentProject();
const { refreshPanelCounts, projectHasActiveFindings } = usePanel();
const selectedTarget = ref<Target | null>(null);
const showReportModal = ref(false);
const notesButton = ref();

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
      cell: ({ row }) => table.valueCell(row.getValue("id")),
    },
    {
      accessorKey: "target",
      header: "Target",
      icon: "i-lucide-locate-fixed",
      cell: ({ row }) => table.valueCell(row.getValue("target")),
    },
    {
      accessorKey: "type",
      header: "Type",
      icon: "i-lucide-tag",
      cell: ({ row }) => {
        const type = row.getValue("type") as string;
        const typeConfig = targetTypes.find((t) => t.value === type);
        return table.badgeCell(
          type,
          typeConfig?.icon || "i-lucide-locate-fixed",
        );
      },
    },
    {
      accessorKey: "target_ports",
      header: "Target Ports",
      icon: "i-lucide-server",
      cell: ({ row }) =>
        table.valueCell(formatCount(row.getValue("target_ports").length || 0)),
    },
    {
      accessorKey: "tasks",
      header: "Scans",
      icon: "i-lucide-play",
      cell: ({ row }) =>
        table.counterCell(
          row.getValue("tasks").length || 0,
          `/projects/${route.params.project_id}/scans?target=${row.original.id}`,
        ),
    },
    {
      accessorKey: "notes",
      header: "Notes",
      icon: "i-lucide-notebook",
      cell: ({ row }) =>
        table.counterCell(
          row.getValue("notes").length || 0,
          `/projects/${route.params.project_id}/notes?target=${row.original.id}`,
        ),
    },
    {
      accessorKey: "reports",
      header: "Reports",
      icon: "i-lucide-file-text",
      cell: ({ row }) =>
        table.linkCell(
          `/projects/${route.params.project_id}/reports?target=${row.original.id}`,
          undefined,
          undefined,
          formatCount(row.getValue("reports").length || 0),
          true,
          "Related reports",
        ),
    },
    ...(showDefectDojo.value
      ? [
          {
            accessorKey: "defectdojo",
            header: "DefectDojo",
            avatar: { src: integrations.defectdojo?.integration?.icon },
            cell: ({ row }) =>
              row.original.defectdojo_sync?.engagement_id
                ? h(resolveComponent("DefectdojoLink"), {
                    entity: "engagement",
                    id: row.original.defectdojo_sync?.engagement_id,
                    size: "sm",
                  })
                : table.noDataCell,
          },
        ]
      : []),
  ],
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
      options: targetTypes,
      labelKey: "value",
    },
  ],
  defaultFilters: { project: route.params.project_id },
  ordering: ["id", "target", "type"],
  defaultOrdering: "-id",
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
  defaultBody: { project: route.params.project_id },
  createForm: resolveComponent("TargetsForm"),
  onCreation: (data: Record<string, unknown>) => {
    if (Array.isArray(data.targets) && data.targets.length === 1) {
      navigateTo(
        `/projects/${route.params.project_id}/targets/${data.targets[0].id}`,
      );
    }
  },
  deleteMessage: (target: Target) =>
    buildDeleteMessage(
      "target",
      target.target,
      "Permanent deletion",
      "All associated data including assets, findings, and scans will be permanently deleted. This action cannot be undone.",
    ),
  canRead: true,
  canEdit: false,
  canCreate: userStore.is_auditor,
  canDelete: userStore.is_auditor,
  customDropdownActions: (target: Target) => [
    ...(target?.tasks.length > 0 && projectHasActiveFindings.value
      ? [
          {
            label: "Generate a report",
            icon: "i-lucide-file-text",
            onSelect: (t: Target) => {
              selectedTarget.value = t;
              showReportModal.value = true;
            },
          },
        ]
      : []),
    {
      label: "Take note",
      icon: "i-lucide-notebook",
      onSelect: () => {
        selectedTarget.value = target;
        return nextTick(() => notesButton.value?.createNote());
      },
    },
  ],
});

onMounted(integrations.fetchDefectDojo);
</script>
