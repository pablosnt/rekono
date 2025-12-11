<template>
  <div class="space-y-4 p-3">
    <UContainer>
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

          <UCollapsible
            v-model:open="openFilters"
            v-if="config.filters?.length"
          >
            <UButton
              :icon="openFilters ? 'i-lucide-filter-x' : 'i-lucide-filter'"
              :color="openFilters ? 'primary' : 'neutral'"
              variant="outline"
            />
            <template #content>
              <CrudFilters :config="config" />
            </template>
          </UCollapsible>

          <UDropdownMenu
            v-if="config.tableColumnsVisibility && config.tableColumns?.length"
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
              <CrudForm :config="config" />
            </template>
            <template #footer="{ close }">
              <UButton
                label="Cancel"
                color="neutral"
                variant="outline"
                @click="close"
              />
              <UButton
                color="primary"
                label="Create"
                @click="
                  emit('create');
                  close($event);
                "
              />
            </template>
          </UModal>
        </div>
      </div>
    </UContainer>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";

const props = defineProps<{
  config: CrudConfig;
  table: any;
  openCreateModal: boolean;
}>();
const emit = defineEmits<{
  search: [search: string];
  filters: [filters: Record<string, unknown>];
  create: [];
  openCreateModal: [open: boolean];
}>();
const utils = useUtils();
const search = ref("");
const openFilters = ref(false);
</script>
