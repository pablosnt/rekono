<template>
  <div>
    <slot name="stats" />
    <CrudPage ref="page" :config="config">
      <template #actions="{ item }">
        <FindingsUtilsNotes :finding="item" :entity-name="entityName" />
        <slot name="extra-actions" :item="item" />
      </template>
    </CrudPage>
    <FindingsModalTriage
      v-if="isTriageable && userStore.is_auditor"
      :open="triageModalOpen"
      :api="api"
      :finding="selectedItem"
      :entity-name="entityName"
      @open="(open) => (triageModalOpen = open)"
      @triaged="page?.fetch()"
    />
    <FindingsModalFix
      v-if="selectedItem && userStore.is_auditor"
      :api="api"
      :fix-verb="fixVerb"
      :unfix-verb="unfixVerb"
      :finding="selectedItem"
      :is-asset="isAsset"
      :entity-name="entityName"
      :open="fixModalOpen"
      @open="(open) => (fixModalOpen = open)"
      @switched="page?.fetch()"
    />
    <UModal
      v-if="selectedItemExposureWindow"
      v-model:open="exposureModalOpen"
      title="Exposure Window"
      description="Dates when the finding has been detected"
      :ui="{ content: 'sm:max-w-3xl sm:max-h-xl' }"
    >
      <template #body>
        <FindingsMetricsExposure
          :finding="selectedItem"
          :dates="selectedItemExposureWindow"
        />
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, DropdownAction } from "~/types/crud";
import { useUserStore } from "~/store/user";
import type { Finding } from "~/types/models";
import { triageStatuses } from "~/constants";

const props = defineProps<{
  endpoint: string;
  entityName: string;
  entityNamePlural: string;
  icon: string;
  columns?: CrudConfig["tableColumns"];
  filters?: CrudConfig["filters"];
  ordering?: CrudConfig["ordering"];
  visibility?: CrudConfig["tableColumnsVisibility"];
  isTriageable?: boolean;
  isAsset?: boolean;
  customFixVerb?: string;
  extraDropdownActions?: (
    item: Record<string, unknown>,
  ) => DropdownAction<Record<string, unknown>>[];
  customDefaultFilters?: Rercord<string, unknown>;
  headerHideTitle?: boolean;
}>();

const userStore = useUserStore();
const options = useOptions();
const route = useRoute();
const api = useApi(props.endpoint);
const table = useTable();
const page = ref();
const selectedItem = ref();
const selectedItemExposureWindow = ref();
const triageModalOpen = ref(false);
const fixModalOpen = ref(false);
const exposureModalOpen = ref(false);
const fixVerb = computed(() =>
  props.customFixVerb ? props.customFixVerb : props.isAsset ? "Dismiss" : "Fix",
);
const unfixVerb = computed(() =>
  fixVerb.value === "Fix" ? "Reopen" : "Restore",
);
const targetOptions = ref();
const taskOptions = ref();
const toolOptions = ref();
const hacktricks = ref();

onMounted(() => {
  options.targets(
    targetOptions,
    route.params.project_id ? { project: route.params.project_id } : undefined,
  );
  options.tasks(
    taskOptions,
    route.params.project_id ? { project: route.params.project_id } : undefined,
  );
  options.tools(toolOptions);
  useApi("/api/integrations/")
    .get("3/")
    .then((response) => (hacktricks.value = response));
});

// todo: DefectDojo link (if integration enabled and available. Get defectdojo server from settings)

const config: CrudConfig<Finding> = reactive({
  endpoint: props.endpoint,
  entityName: props.entityName,
  entityNamePlural: props.entityNamePlural,
  icon: props.icon,
  headerHideTitle: props.headerHideTitle || false,
  itemLink: (finding: Finding) =>
    `/projects/${finding.project}/${props.entityNamePlural.toLowerCase()}/${finding.id}`,
  get tableColumns() {
    return [
      {
        accessorKey: "id",
        header: "ID",
        icon: "i-lucide-hash",
        cell: ({ row }) => table.valueCell(row.getValue("id")),
      },
      ...(props.columns || []),
      {
        accessorKey: "status",
        header: "Status",
        icon: "i-lucide-activity",
        cell: ({ row }) =>
          h(resolveComponent("FindingsUtilsStatus"), {
            finding: row.original,
            isTriageable: props.isTriageable,
            fixVerb: fixVerb.value,
          }),
      },
      ...(props.isTriageable
        ? [
            {
              accessorKey: "triage",
              header: "Triage Comment",
              icon: "i-lucide-message-circle-more",
              cell: ({ row }) => table.valueCell(row.original.triage_comment),
            },
          ]
        : []),
      {
        accessorKey: "scanners",
        header: "Scanners",
        icon: "i-lucide-toolbox",
        cell: ({ row }) => {
          if (row.original.created_from_user_input) {
            return h(
              resolveComponent("UTooltip"),
              {
                text: `${props.isAsset ? "Asset" : "Finding"} automatically created from user-provided data to keep relationships between findings consistent`,
              },
              {
                default: () =>
                  h(resolveComponent("UButton"), {
                    icon: "i-lucide-user-cog",
                    color: "neutral",
                    variant: "ghost",
                    label: "User input",
                    class: "font-medium text-sm",
                  }),
              },
            );
          }
          const scanners = row.original.executions
            .map((e) => {
              return {
                name: e.configuration.tool.name,
                icon: e.configuration.tool.icon,
              };
            })
            .filter(
              (value, index, self) =>
                index === self.findIndex((e) => e.name === value.name),
            );
          return h(
            "div",
            { class: "flex items-center gap-1.5" },
            scanners.map((s) =>
              h(
                resolveComponent("UChip"),
                {
                  text: row.original.executions
                    .filter((e) => e.configuration?.tool.name === s.name)
                    .length.toString(),
                  size: "3xl",
                  color: "neutral",
                  variant: "ghost",
                },
                {
                  default: () =>
                    h(
                      resolveComponent("UTooltip"),
                      {
                        text: s.name,
                        content: {
                          side: "right",
                          sideOffset: 8,
                          collisionPadding: 8,
                        },
                      },
                      {
                        default: () =>
                          h(resolveComponent("UButton"), {
                            avatar: s.icon ? { src: s.icon } : undefined,
                            icon: s.icon
                              ? undefined
                              : "i-lucide-square-terminal",
                          }),
                      },
                    ),
                },
              ),
            ),
          );
        },
      },
      {
        accessorKey: "exposure",
        header: "Exposure Window",
        icon: "i-lucide-history",
        cell: ({ row }) => {
          const dates = getExposureWindow(row.original);
          if (dates.length === 0) return table.noDataCell;
          else if (dates.length === 1)
            return table.valueCell(dates[0].date.toDateString());
          else {
            return h(resolveComponent("UButton"), {
              label: `${dates[0].date.toDateString()} - ${dates[dates.length - 1].date.toDateString()}`,
              color: "neutral",
              variant: "ghost",
              onClick: () => {
                selectedItem.value = row.original;
                selectedItemExposureWindow.value = dates;
                exposureModalOpen.value = true;
              },
            });
          }
        },
      },
      ...(hacktricks.value?.enabled
        ? [
            {
              accessorKey: "hacktricks",
              header: "HackTricks",
              avatar: { src: hacktricks.value.icon },
              cell: ({ row }) =>
                table.externalLinkCell(
                  row.original.hacktricks_link,
                  undefined,
                  hacktricks.value.icon,
                ),
            },
          ]
        : []),
    ];
  },
  tableColumnsVisibility: Object.assign({}, props.visibility || {}, {
    id: false,
    triage: false,
  }),
  searchable: true,
  searchPlaceholder: `Search ${smartLowerCase(props.entityNamePlural)}...`,
  get filters() {
    return [
      {
        key: "target",
        label: "Target",
        icon: "i-lucide-locate-fixed",
        type: "select" as const,
        options: targetOptions,
      },
      {
        key: "task",
        label: "Task",
        icon: "i-lucide-play",
        type: "select" as const,
        options: taskOptions,
      },
      {
        key: "tool",
        label: "Tool",
        icon: "i-lucide-square-terminal",
        type: "select" as const,
        options: toolOptions,
      },
      ...(props.filters || []),
      ...(props.isTriageable
        ? [
            {
              key: "triage_status",
              label: "Triage Status",
              icon: "i-lucide-shield-check",
              type: "select",
              options: triageStatuses,
              labelKey: "value",
            },
          ]
        : []),
      {
        key: "is_fixed",
        label: `${fixVerb.value}ed`,
        type: "checkbox",
      },
      {
        key: "auto_fixed",
        label: `Auto-${fixVerb.value}ed`,
        type: "checkbox",
      },
      {
        key: "created_from_user_input",
        label: "From user input",
        type: "checkbox",
      },
    ];
  },
  defaultFilters:
    props.customDefaultFilters || route.params.project_id
      ? { project: route.params.project_id }
      : undefined,
  ordering: props.ordering || [],
  defaultOrdering: "-id",
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
  tableCopyId: true,
  canRead: true,
  canCreate: false,
  canEdit: false,
  canDelete: false,
  customDropdownActions: (item: Finding) => {
    const actions = userStore.is_auditor
      ? getFindingDropdownActions(
          item,
          fixVerb.value,
          unfixVerb.value,
          props.isTriageable,
          (item) => {
            selectedItem.value = item;
            fixModalOpen.value = true;
          },
          (item) => {
            selectedItem.value = item;
            fixModalOpen.value = true;
          },
          (item) => {
            selectedItem.value = item;
            triageModalOpen.value = true;
          },
        )
      : [];
    if (props.extraDropdownActions) {
      actions.push(...props.extraDropdownActions(item));
    }
    return actions;
  },
});

defineExpose({ fetch: () => page.value?.fetch() });
</script>
