<template>
  <div class="space-y-4 p-3">
      <UBreadcrumb
        v-if="config.breadcrumbs?.length"
        :items="config.breadcrumbs"
      />
      <div class="flex flex-wrap items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-default">
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
            :items="
              config.ordering?.map((ordering: string) => ({
                id: ordering,
                label: ordering === 'id' ? 'ID' : utils.firstUpper(ordering),
              }))
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
                        state.ordering === item.id ? 'primary' : 'neutral'
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
                  label:
                    column.id === 'id' ? 'ID' : utils.firstUpper(column.id),
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

          <UModal
            v-if="config.canCreate"
            :open="openCreateModal"
            :title="`New ${config.entityName}`"
            :ui="{ content: 'sm:max-w-3xl sm:max-h-xl', footer: 'justify-end' }"
            @update:open="(open) => $emit('openCreateModal', open)"
          >
            <UButton
              icon="i-lucide-plus"
              @click="$emit('openCreateModal', true)"
            />
            <template #body>
              <CrudForm
                ref="form"
                :api="api"
                :config="config"
                @submit="
                  emit('create');
                  $emit('openCreateModal', false);
                "
              />
            </template>
            <template #footer="{ close }">
              <UButton
                label="Cancel"
                color="neutral"
                variant="outline"
                @click="close"
              />
              <UButton color="primary" label="Create" @click="form.submit()" />
            </template>
          </UModal>
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
  api: any;
  config: CrudConfig;
  state: CrudState;
  table: any;
  openCreateModal: boolean;
}>();
const emit = defineEmits<{
  search: [search: string];
  filters: [filters: Record<string, unknown>];
  ordering: [sortering: string];
  create: [];
  openCreateModal: [open: boolean];
}>();
const utils = useUtils();
const search = ref("");
const openFilters = ref(false);
const form = ref();
</script>
