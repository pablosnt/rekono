<template>
  <UEmpty
    :title="`No ${smartLowerCase(config.entityNamePlural)} found`"
    :description="description"
    :icon="config.icon"
    :actions="actions"
    size="xl"
    variant="naked"
  />
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";

const props = defineProps<{
  config: CrudConfig;
  state: Record<string, unknown>;
  onCreate?: () => unknown;
}>();

const description = computed(() => {
  if (
    Object.keys(props.state.filters as object).length >
      Object.keys(props.config.defaultFilters || {}).length ||
    props.state.searchQuery
  ) {
    return `The current search criteria don't match any ${smartLowerCase(props.config.entityName)}. Change your query and retry`;
  }
  const base =
    props.config.emptyMessage ||
    `There are no ${smartLowerCase(props.config.entityNamePlural)} yet`;
  return props.config.canCreate ? `${base}. You can create one below` : base;
});
const actions = computed(() => {
  return props.config.canCreate
    ? [
        {
          icon: "i-lucide-plus",
          label: "Create new",
          loadingAuto: true,
          onClick: () => props.onCreate?.(),
        },
      ]
    : [];
});
</script>
