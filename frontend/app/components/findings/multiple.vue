<template>
  <div class="min-w-0">
    <CrudPage ref="page" :config="config" :disable-url-sync="disableUrlSync">
      <template v-if="linkToOriginalPage" #header-extra-actions>
        <UTooltip :text="`Go to ${smartLowerCase(entityNamePlural)} page`">
          <UButton
            icon="i-lucide-external-link"
            :to="linkToOriginalPage"
            target="_blank"
            variant="outline"
            color="neutral"
            :aria-label="`${firstUpper(smartLowerCase(entityNamePlural))} page`"
          />
        </UTooltip>
      </template>
      <template #actions="{ item }">
        <NotesDropdown
          :related-entity="item"
          :entity-name="entityName"
          :project="item.project"
        />
        <slot name="extra-actions" :item="item" />
      </template>
    </CrudPage>
    <LazyFindingsModalTriage
      v-if="isTriageable && userStore.is_auditor"
      :open="triageModalOpen"
      :api="api"
      :finding="selectedItem"
      :entity-name="entityName"
      @open="(open) => (triageModalOpen = open)"
      @triaged="page?.fetch()"
    />
    <LazyFindingsModalFix
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
    <LazyUModal
      v-if="selectedItemExposureWindow"
      v-model:open="exposureModalOpen"
      title="Exposure Window"
      :description="
        selectedItem.executions.length > 0
          ? `First detected ${useTimeAgo(new Date(selectedItemExposureWindow[0].date)).value} across ${selectedItem.executions.length} executions${selectedItem.is_fixed ? `. ${firstUpper(fixVerb)}ed ${useTimeAgo(new Date(selectedItem.fixed_date)).value}` : ''}`
          : 'Dates when the finding has been detected'
      "
      :ui="{ content: 'sm:max-w-3xl sm:max-h-xl' }"
    >
      <template #body>
        <FindingsExposure
          :finding="selectedItem"
          :dates="selectedItemExposureWindow"
        />
      </template>
    </LazyUModal>
  </div>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, DropdownAction } from "~/types/crud";
import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";
import type { Finding } from "~/types/models";
import { triageStatuses } from "~/constants";
import { useTimeAgo } from "@vueuse/core";

const props = defineProps<{
  endpoint: string;
  entityName: string;
  entityNamePlural: string;
  icon: string;
  columns?: CrudConfig["tableColumns"];
  filters?: CrudConfig["filters"];
  acceptedFilters?: CrudConfig["acceptedFilters"];
  ordering?: CrudConfig["ordering"];
  visibility?: CrudConfig["tableColumnsVisibility"];
  isTriageable?: boolean;
  isAsset?: boolean;
  hasHacktricks?: boolean;
  customFixVerb?: string;
  extraDropdownActions?: (
    item: Record<string, unknown>,
  ) => DropdownAction<Record<string, unknown>>[];
  customDefaultFilters?: Rercord<string, unknown>;
  headerHideTitle?: boolean;
  disableUrlSync?: boolean;
  linkToOriginalPage?: string;
}>();

const userStore = useUserStore();
const integrations = useIntegrationsStore();
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
const toolOptions = ref();

onMounted(() => {
  options.targets(
    targetOptions,
    route.params.project_id ? { project: route.params.project_id } : undefined,
  );
  options.tools(toolOptions);
  if (props.hasHacktricks) integrations.fetchHackTricks();
});

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
          h(resolveComponent("FindingsStatus"), {
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
            { class: "flex items-center gap-3.5" },
            scanners.map((s) =>
              h(
                resolveComponent("UChip"),
                {
                  text: formatCount(
                    row.original.executions.filter(
                      (e) => e.configuration?.tool.name === s.name,
                    ).length,
                  ),
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
                          s.icon
                            ? h(resolveComponent("UAvatar"), {
                                src: s.icon,
                                size: "sm",
                                alt: s.name,
                                "aria-label": s.name,
                              })
                            : h(resolveComponent("UIcon"), {
                                name: "i-lucide-square-terminal",
                                "aria-label": s.name,
                                class: "text-xl text-primary",
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
          return dates.length === 1
            ? h(
                "span",
                {
                  class:
                    "inline-flex items-center font-medium px-2.5 py-1.5 text-sm",
                },
                dates[0].date.toDateString(),
              )
            : h(resolveComponent("UButton"), {
                label: `${dates[0].date.toDateString()} - ${dates.at(-1).date.toDateString()}`,
                color: "neutral",
                variant: "ghost",
                onClick: () => {
                  selectedItem.value = row.original;
                  selectedItemExposureWindow.value = dates;
                  exposureModalOpen.value = true;
                },
              });
        },
      },
      ...(props.hasHacktricks && integrations.hacktricks?.enabled
        ? [
            {
              accessorKey: "hacktricks",
              header: "HackTricks",
              avatar: { src: integrations.hacktricks.icon },
              cell: ({ row }) =>
                table.externalLinkCell(
                  row.original.hacktricks_link,
                  undefined,
                  integrations.hacktricks?.icon,
                  undefined,
                  "HackTricks",
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
  get acceptedFilters() {
    return [
      {
        key: "task",
        label: "Task",
        icon: "i-lucide-play",
        loadOption: (value: string | number) => options.task(value),
      },
      ...(props.acceptedFilters || []),
    ];
  },
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
        label: "Status",
        icon: "i-lucide-activity",
        type: "select" as const,
        options: [
          { label: "Open", value: "false", icon: "i-lucide-shield-alert" },
          {
            label: `${fixVerb.value}ed`,
            value: "true",
            icon:
              fixVerb.value === "Fix"
                ? "i-lucide-badge-check"
                : "i-lucide-eye-off",
          },
        ],
      },
      {
        key: "created_from_user_input",
        label: "Origin",
        icon: "i-lucide-toolbox",
        type: "select" as const,
        options: [
          {
            label: "Detected",
            value: "false",
            icon: "i-lucide-square-terminal",
          },
          { label: "User input", value: "true", icon: "i-lucide-user-cog" },
        ],
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
          (f) => {
            selectedItem.value = f;
            fixModalOpen.value = true;
          },
          (f) => {
            selectedItem.value = f;
            fixModalOpen.value = true;
          },
          (f) => {
            selectedItem.value = f;
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
