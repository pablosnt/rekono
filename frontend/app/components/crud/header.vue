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
            icon="i-lucide-search"
            class="w-full min-w-48 sm:w-64"
            @update:model-value="
              () => {
                $emit('search', search);
                if (search && !disableUrlSync)
                  router.replace({ query: { ...route.query, ...{ search } } });
              }
            "
          />
          <UButton
            v-if="config.filters?.length"
            :icon="openFilters ? 'i-lucide-filter-x' : 'i-lucide-filter'"
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
              config.ordering?.map(
                (ordering: string | { id: string; label: string }) => {
                  const id =
                    typeof ordering === 'string' ? ordering : ordering.id;
                  const label =
                    typeof ordering === 'string'
                      ? firstUpper(smartLowerCase(ordering))
                      : ordering.label;
                  return { id, label };
                },
              )
            "
            :content="{ align: 'end' }"
          >
            <UButton
              icon="i-lucide-arrow-up-down"
              color="neutral"
              variant="outline"
            />
            <template #item="{ item }">
              <div class="flex items-center justify-between flex-1 gap-2">
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
            />
          </UDropdownMenu>

          <slot v-if="config.canCreate" name="create-button">
            <CrudFormModal
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
            <UButton icon="i-lucide-plus" @click="$emit('openCreate', true)" />
          </slot>
        </slot>
      </div>
    </div>
    <UCollapsible v-model:open="openFilters">
      <template #content>
        <CrudFilters
          :config="config"
          :state="state"
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

const route = useRoute();
const router = useRouter();
const search = ref(props.state?.searchQuery ?? "");
const openFilters = ref(props.filtersOpen ?? false);

function columnLabel(columnId: string): string {
  const colDef = props.config.tableColumns?.find(
    (c) => (c as { accessorKey?: string }).accessorKey === columnId,
  );
  return typeof colDef?.header === "string"
    ? colDef.header
    : firstUpper(smartLowerCase(columnId));
}
</script>
