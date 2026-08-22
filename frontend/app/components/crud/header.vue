<template>
  <div class="space-y-4 p-3">
    <div
      class="flex flex-row flex-wrap items-center justify-between gap-4 w-full"
    >
      <div class="flex flex-row justify-start items-center gap-4">
        <slot name="header-leading" />
        <UIcon
          :name="config.headerIcon"
          :class="titleSizeClass ? titleSizeClass : 'text-2xl'"
          :aria-label="config.entityNamePlural"
        />
        <h1
          v-if="!config.headerHideTitle"
          :class="[
            'font-bold text-default truncate max-w-[300px] sm:max-w-none',
            titleSizeClass ? titleSizeClass : 'text-2xl',
          ]"
        >
          {{ config.entityNamePlural }}
        </h1>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <slot name="header-actions">
          <UInput
            v-if="config.searchable"
            v-model="search"
            :placeholder="config.searchPlaceholder"
            :aria-label="config.searchPlaceholder || 'Search'"
            icon="i-lucide-search"
            class="w-full min-w-48 sm:w-64"
            @update:model-value="$emit('search', search)"
          >
            <template v-if="search" #trailing>
              <UButton
                icon="i-lucide-x"
                variant="ghost"
                color="neutral"
                size="sm"
                aria-label="Clear search"
                @click="
                  search = '';
                  $emit('search', '');
                "
              />
            </template>
          </UInput>
          <UButton
            v-if="config.filters?.length"
            :icon="openFilters ? 'i-lucide-filter-x' : 'i-lucide-filter'"
            :aria-label="openFilters ? 'Close filters' : 'Open filters'"
            :color="openFilters ? 'primary' : 'neutral'"
            variant="outline"
            @click="
              openFilters = !openFilters;
              !openFilters
                ? emit(
                    'filters',
                    config.defaultFilters
                      ? JSON.parse(JSON.stringify(config.defaultFilters))
                      : {},
                  )
                : null;
            "
          />

          <UDropdownMenu
            v-if="config.ordering?.length"
            :items="
              !orderingOptions.some(
                ({ id }) =>
                  id === config.defaultOrdering ||
                  `-${id}` === config.defaultOrdering,
              )
                ? [
                    [
                      {
                        id: '__default__',
                        label: 'Default order',
                        isDefault: true,
                      },
                    ],
                    orderingOptions,
                  ]
                : orderingOptions
            "
            :content="{ align: 'end' }"
          >
            <UButton
              icon="i-lucide-arrow-up-down"
              color="neutral"
              variant="outline"
              aria-label="Sort results"
            />
            <template #item="{ item }">
              <div
                v-if="item.isDefault"
                class="flex items-center justify-between flex-1 gap-2 cursor-pointer"
                @click.stop="emit('ordering', config.defaultOrdering)"
              >
                <span class="text-sm font-medium">{{ item.label }}</span>
                <UIcon
                  v-if="state?.ordering === config.defaultOrdering"
                  name="i-lucide-check"
                  class="size-4 text-primary"
                />
              </div>
              <div
                v-else
                class="flex items-center justify-between flex-1 gap-2"
              >
                <span class="text-sm font-medium">{{ item.label }}</span>
                <div class="flex items-center gap-1">
                  <UTooltip text="Ascending">
                    <UButton
                      size="xs"
                      :color="
                        state?.ordering === item.id ? 'primary' : 'neutral'
                      "
                      variant="soft"
                      icon="i-lucide-arrow-up-narrow-wide"
                      :aria-label="`Sort by ${item.label} ascending`"
                      @click.stop="emit('ordering', item.id)"
                    />
                  </UTooltip>
                  <UTooltip text="Descending">
                    <UButton
                      size="xs"
                      :color="
                        state?.ordering === `-${item.id}`
                          ? 'primary'
                          : 'neutral'
                      "
                      variant="soft"
                      icon="i-lucide-arrow-down-wide-narrow"
                      :aria-label="`Sort by ${item.label} descending`"
                      @click.stop="emit('ordering', `-${item.id}`)"
                    />
                  </UTooltip>
                </div>
              </div>
            </template>
          </UDropdownMenu>

          <UDropdownMenu
            v-if="
              table &&
              config.tableColumnsVisibility &&
              config.tableColumns?.length
            "
            :items="
              table?.tableApi
                ?.getAllColumns()
                .filter((column) => column.getCanHide())
                .map((column) => ({
                  label: columnLabel(column.id),
                  type: 'checkbox' as const,
                  checked: column.getIsVisible(),
                  onUpdateChecked(checked: boolean) {
                    table?.tableApi
                      ?.getColumn(column.id)
                      ?.toggleVisibility(!!checked);
                  },
                  onSelect(e: Event) {
                    e.preventDefault();
                  },
                }))
            "
            :content="{ align: 'end' }"
          >
            <UButton
              icon="i-lucide-settings-2"
              color="neutral"
              variant="outline"
              aria-label="Show or hide columns"
            />
          </UDropdownMenu>

          <slot v-if="config.canCreate" name="create-button">
            <LazyCrudFormModal
              :open="openCreateModal"
              :api="api"
              :config="config"
              :submit-label="config.createLabel"
              @open="
                (open: boolean) => {
                  $emit('openCreate', open);
                  if (!open && config.updateOnCreateModalOpen) {
                    $emit('create');
                  }
                }
              "
              @submit="emit('create')"
            />
            <UButton
              icon="i-lucide-plus"
              :aria-label="`Create ${config.entityName}`"
              @click="$emit('openCreate', true)"
            />
          </slot>

          <slot name="header-extra-actions" />
        </slot>
      </div>
    </div>
    <UCollapsible v-model:open="openFilters">
      <template #content>
        <LazyCrudFilters
          :config="config"
          :state="state"
          :disable-url-sync="disableUrlSync"
          @filters="(filters) => $emit('filters', filters)"
        />
      </template>
    </UCollapsible>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState } from "~/types/crud";

const props = defineProps<{
  api: typeof useApi;
  config: CrudConfig;
  state?: CrudState;
  table?: unknown;
  openCreateModal?: boolean;
  titleSizeClass?: string;
  filtersOpen?: boolean;
  disableUrlSync?: boolean;
}>();
const emit = defineEmits<{
  search: [search: string];
  filters: [filters: Record<string, unknown>];
  ordering: [sortering: string];
  create: [];
  openCreate: [open: boolean];
}>();

const search = ref(props.state?.searchQuery ?? "");
const openFilters = ref(props.filtersOpen ?? false);
const orderingOptions = computed(() =>
  (props.config.ordering ?? []).map(
    (ordering: string | { id: string; label: string }) => {
      const id = typeof ordering === "string" ? ordering : ordering.id;
      const label =
        typeof ordering === "string"
          ? firstUpper(smartLowerCase(ordering))
          : ordering.label;
      return { id, label };
    },
  ),
);

function columnLabel(columnId: string): string {
  const colDef = props.config.tableColumns?.find(
    (c) => (c as { accessorKey?: string }).accessorKey === columnId,
  );
  return typeof colDef?.header === "string"
    ? colDef.header
    : firstUpper(smartLowerCase(columnId));
}
</script>
