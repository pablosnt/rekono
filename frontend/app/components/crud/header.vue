<template>
  <div class="space-y-4 p-3">
    <UBreadcrumb
      v-if="config.breadcrumbs?.length"
      :items="config.breadcrumbs"
    />
    <div class="flex flex-row items-center justify-between gap-4 w-full">
      <div class="flex-none">
        <h1
          class="text-2xl font-bold text-default truncate max-w-[300px] sm:max-w-none"
        >
          {{ config.entityNamePlural }}
        </h1>
      </div>

      <div class="flex items-center gap-3">
        <UInput
          v-if="config.searchable"
          v-model="search"
          :placeholder="config.searchPlaceholder"
          icon="i-lucide-search"
          class="w-64"
          @update:model-value="$emit('search', search)"
        />

        <UButton
          v-if="config.filters?.length"
          :icon="openFilters ? 'i-lucide-filter-x' : 'i-lucide-filter'"
          :color="openFilters ? 'primary' : 'neutral'"
          variant="outline"
          @click="
            openFilters = !openFilters;
            !openFilters ? emit('filters', {}) : null;
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
                    ? ordering === 'id'
                      ? 'ID'
                      : utils.firstUpper(ordering)
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
                    :color="state.ordering === item.id ? 'primary' : 'neutral'"
                    variant="soft"
                    icon="i-lucide-arrow-up-narrow-wide"
                    @click.stop="emit('ordering', item.id)"
                  />
                </UTooltip>
                <UTooltip text="Descending">
                  <UButton
                    size="xs"
                    :color="
                      state.ordering === `-${item.id}` ? 'primary' : 'neutral'
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
                label: column.id === 'id' ? 'ID' : utils.firstUpper(column.id),
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

        <CrudFormModal
          v-if="config.canCreate"
          :open="openCreateModal"
          :api="api"
          :config="config"
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
          v-if="config.canCreate"
          icon="i-lucide-plus"
          @click="$emit('openCreate', true)"
        />
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

defineProps<{
  api: object;
  config: CrudConfig;
  state: CrudState;
  table: unknown;
  openCreateModal: boolean;
}>();
const emit = defineEmits<{
  search: [search: string];
  filters: [filters: Record<string, unknown>];
  ordering: [sortering: string];
  create: [];
  openCreate: [open: boolean];
}>();
const utils = useUtils();
const search = ref("");
const openFilters = ref(false);
</script>
