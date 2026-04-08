<template>
  <div>
    <slot name="stats" />
    <CrudPage ref="page" :config="config">
      <template #actions="{ item }">
        <UDropdownMenu
          v-if="userStore.is_auditor || item.notes.length > 0"
          :items="
            [
              item.notes.length > 0
                ? {
                    label: `${item.notes.length} Notes`,
                    icon: 'i-lucide-notebook',
                    color: 'neutral',
                    to: `/projects/${item.project}/notes?${entityNamePlural.toLowerCase()}=${item.id}`,
                  }
                : {},
              userStore.is_auditor
                ? {
                    label: 'Take note',
                    icon: 'i-lucide-plus',
                    color: 'neutral',
                    onSelect: () => {
                      selectedItem = item;
                      nextTick(() => notesButton.value?.createNote());
                    },
                  }
                : {},
            ].filter((i) => Object.keys(i).length > 0)
          "
          :content="{ align: 'end' }"
        >
          <UButton icon="i-lucide-notebook" variant="ghost" color="neutral" />
        </UDropdownMenu>
        <slot name="extra-actions" :item="item" />
      </template>
    </CrudPage>
    <NotesButton
      v-if="selectedItem && userStore.is_auditor"
      ref="notesButton"
      :show="false"
      v-bind="noteProps"
    />
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
  </div>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig, DropdownAction } from "~/types/crud";
import { useUserStore } from "~/store/user";
import { useTimeAgo } from "@vueuse/core";
import type { Finding } from "~/types/models";
import { triageStatuses } from "~/constants";

const props = defineProps<{
  endpoint: string;
  entityName: string;
  entityNamePlural: string;
  icon: string;
  columns: CrudConfig["tableColumns"];
  filters: CrudConfig["filters"];
  ordering: CrudConfig["ordering"];
  visibility: CrudConfig["tableColumnsVisibility"];
  isTriageable?: boolean;
  isAsset?: boolean;
  extraDropdownActions?: (
    item: Record<string, unknown>,
  ) => DropdownAction<Record<string, unknown>>[];
}>();

const userStore = useUserStore();
const options = useOptions();
const route = useRoute();
const api = useApi(props.endpoint);
const page = ref();
const selectedItem = ref();
const triageModalOpen = ref(false);
const fixModalOpen = ref(false);
const fixVerb = ref(props.isAsset ? "Dismiss" : "Fix");
const unfixVerb = ref(props.isAsset ? "Restore" : "Reopen");
const notesButton = ref();
const targetOptions = ref();
const taskOptions = ref();
const toolOptions = ref();

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
});

const noteProps = computed(() => {
  if (!selectedItem.value) return {};
  return { [props.entityName.toLowerCase()]: selectedItem.value.id };
});

// TODO: First and last execution date (maybe a column "Exposure Window" that opens a modal with an evolution graph of executions detecting it per date)
// todo: DefectDojo link

const config: CrudConfig<Finding> = reactive({
  endpoint: props.endpoint,
  entityName: props.entityName,
  entityNamePlural: props.entityNamePlural,
  icon: props.icon,
  itemLink: (finding: Finding) =>
    `/projects/${finding.project}/${props.entityNamePlural.toLowerCase()}/${finding.id}`,
  tableColumns: [
    {
      accessorKey: "id",
      header: "ID",
      icon: "i-lucide-hash",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("id")),
    },
    ...props.columns,
    {
      accessorKey: "status",
      header: "Status",
      icon: "i-lucide-activity",
      cell: ({ row }) => {
        const finding = row.original;
        if (finding.is_fixed) {
          return h(
            resolveComponent("UTooltip"),
            {
              text: finding.auto_fixed
                ? "Auto-Fixed"
                : `Fixed by ${finding.fixed_by.username} ${useTimeAgo(new Date(finding.fixed_date)).value}`,
              content: { side: "left", sideOffset: 8, collisionPadding: 8 },
            },
            {
              default: () =>
                h(resolveComponent("UButton"), {
                  icon: finding.auto_fixed
                    ? "i-lucide-bot"
                    : "i-lucide-badge-check",
                  color: "success",
                  variant: "ghost",
                  label: "Fixed",
                  class: "font-medium text-sm",
                }),
            },
          );
        } else if (props.isTriageable) {
          const config = triageStatuses.find(
            (s) => s.value === finding.triage_status,
          );
          return finding.triage_by && finding.triage_date
            ? h(
                resolveComponent("UTooltip"),
                {
                  text: `Triaged by ${finding.triage_by.username} ${useTimeAgo(new Date(finding.triage_date)).value}`,
                  content: { side: "left", sideOffset: 8, collisionPadding: 8 },
                },
                {
                  default: () =>
                    h(resolveComponent("UButton"), {
                      icon: config?.icon,
                      color: config?.color,
                      variant: "ghost",
                      label: config?.value,
                      class: "font-medium text-sm",
                    }),
                },
              )
            : h(
                resolveComponent("UBadge"),
                {
                  color: config?.color,
                  variant: "ghost",
                  class: "font-medium",
                },
                {
                  default: () => [
                    h(resolveComponent("UIcon"), {
                      name: config?.icon,
                      class: "mr-1 text-lg",
                    }),
                    config?.value,
                  ],
                },
              );
        } else {
          return h(
            resolveComponent("UBadge"),
            {
              color: "neutral",
              variant: "ghost",
              class: "font-medium",
            },
            {
              default: () => [
                h(resolveComponent("UIcon"), {
                  name: "i-lucide-shield-alert",
                  class: "mr-1 text-lg",
                }),
                "Active",
              ],
            },
          );
        }
      },
    },
    {
      accessorKey: "triage",
      header: "Triage Comment",
      icon: "i-lucide-message-circle-more",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.original.triage_comment),
    },
    {
      accessorKey: "scanners",
      header: "Scanners",
      icon: "i-lucide-toolbox",
      cell: ({ row }) => {
        const finding = row.original;
        if (finding.created_from_user_input) {
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
        const scanners = finding.executions
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
                text: finding.executions
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
                    { text: s.name },
                    {
                      default: () =>
                        h(resolveComponent("UButton"), {
                          avatar: s.icon ? { src: s.icon } : undefined,
                          icon: s.icon ? undefined : "i-lucide-square-terminal",
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
      accessorKey: "hacktricks",
      header: "HackTricks",
      avatar: { src: "https://book.hacktricks.wiki/en/favicon.svg" },
      cell: ({ row }) => {
        const link = row.original.hacktricks_link as string;
        if (!link) return null;
        return h(
          "a",
          {
            href: link,
            target: "_blank",
            rel: "noopener noreferrer",
            class: "text-primary hover:underline",
            onClick: (e: Event) => e.stopPropagation(),
          },
          [
            h(resolveComponent("UIcon"), {
              name: "i-lucide-external-link",
              class: "text-lg",
            }),
          ],
        );
      },
    },
  ],
  tableColumnsVisibility: Object.assign({}, props.visibility || {}, {
    id: false,
    triage: false,
    hacktricks: false,
  }),
  searchable: true,
  searchPlaceholder: `Search ${smartLowerCase(props.entityNamePlural)}...`,
  filters: [
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
    ...props.filters,
    {
      key: "triage_status",
      label: "Triage Status",
      icon: "i-lucide-shield-check",
      type: "select",
      options: triageStatuses,
      labelKey: "value",
    },
    {
      key: "is_fixed",
      label: "Fixed",
      type: "checkbox",
    },
    {
      key: "auto_fixed",
      label: "Auto-Fixed",
      type: "checkbox",
    },
    {
      key: "created_from_user_input",
      label: "From user input",
      type: "checkbox",
    },
  ],
  defaultFilters: route.params.project_id
    ? { project: route.params.project_id }
    : undefined,
  ordering: props.ordering,
  defaultOrdering: "-id",
  pageSize: 25,
  pageSizeOptions: [25, 50, 100],
  tableCopyId: true,
  canRead: true,
  canCreate: false,
  canEdit: false,
  canDelete: false,
  customDropdownActions: (item: Finding) => {
    const actions: DropdownAction<Record<string, unknown>>[] = [];
    if (props.extraDropdownActions) {
      actions.push(...props.extraDropdownActions(item));
    }
    if (userStore.is_auditor) {
      if (!item.is_fixed) {
        actions.push({
          label: fixVerb.value,
          icon: props.isAsset ? "i-lucide-eye-off" : "i-lucide-check-circle",
          color: "success",
          onSelect: (item) => {
            selectedItem.value = item;
            fixModalOpen.value = true;
          },
        });
      } else if (!item.auto_fixed) {
        actions.push({
          label: unfixVerb.value,
          icon: props.isAsset ? "i-lucide-eye" : "i-lucide-rotate-ccw",
          color: "neutral",
          onSelect: (item) => {
            selectedItem.value = item;
            fixModalOpen.value = true;
          },
        });
      }
      if (props.isTriageable && !item.is_fixed) {
        actions.push({
          label: "Triage",
          icon: "i-lucide-shield-check",
          onSelect: (item) => {
            selectedItem.value = item;
            triageModalOpen.value = true;
          },
        });
      }
    }
    return actions;
  },
});

defineExpose({ fetch: () => page.value?.fetch() });
</script>
