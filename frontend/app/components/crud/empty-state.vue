<template>
  <UEmpty
    :title="`No ${utils.smartLowerCase(config.entityNamePlural)} found`"
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
}>();
const emit = defineEmits<{
  createClick: [];
}>();
const utils = useUtils();

const description = computed(() => {
  if (
    Object.keys(props.state.filters as object).length >
      Object.keys(props.config.defaultFilters || {}).length ||
    props.state.searchQuery
  ) {
    return `The current search criteria don't match any ${utils.smartLowerCase(props.config.entityName)}. Change your query and retry`;
  }
  const base =
    props.config.emptyMessage ||
    `It looks like you don't have access to any ${utils.smartLowerCase(props.config.entityName)} yet`;
  const createText = props.config.canCreate
    ? "You can create one below."
    : "Please contact your administrator.";
  return `${base}. ${createText}`;
});

const actions = computed(() => {
  return props.config.canCreate
    ? [
        {
          icon: "i-lucide-plus",
          label: "Create new",
          onClick: () => {
            emit("createClick");
          },
        },
      ]
    : [];
});
</script>
