<template>
  <div class="border-b border-default bg-muted/30 p-4 space-y-4">
    <div class="flex flex-wrap gap-4 justify-between">
      <template v-for="filter in config.filters" :key="filter.key">
        <USelect
          v-if="filter.type === 'select'"
          :model-value="filters[filter.key] as AcceptableValue | undefined"
          :placeholder="filter.placeholder || filter.label"
          :options="getOptions(filter)"
          value-key="value"
          option-key="label"
          class="w-64"
          @update:model-value="(value) => updateFilter(filter.key, value)"
        />
        <UInput
          v-else-if="filter.type === 'text'"
          :model-value="filters[filter.key] as string"
          :placeholder="filter.placeholder || filter.label"
          :icon="filter.icon"
          class="w-64"
          @update:model-value="(value) => updateFilter(filter.key, value)"
        />
        <UCheckbox
          v-else-if="filter.type === 'boolean'"
          :model-value="
            (filter.value
              ? filters[filter.key] === filter.value
              : filters[filter.key]) as boolean
          "
          :label="filter.label"
          class="w-64 items-center"
          @update:model-value="
            (value) =>
              updateFilter(
                filter.key,
                filter.value ? (value === true ? filter.value : null) : value,
              )
          "
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AcceptableValue } from "@nuxt/ui/runtime/types/utils.js";
import type {
  CrudConfig,
  FilterConfig,
  FilterOption,
  CrudState,
} from "~/types/crud";

const props = defineProps<{
  config: CrudConfig;
  state: CrudState;
}>();
const emit = defineEmits<{
  filters: [filters: Record<string, unknown>];
}>();
const filters = ref(props.state.filters);

function getOptions(filter: FilterConfig): FilterOption[] {
  return Array.isArray(filter.options) ? filter.options : [];
}

function updateFilter(key: string, value: unknown) {
  if (value !== null && value !== undefined && value !== "") {
    filters.value[key] = value;
  } else {
    delete filters.value[key];
  }
  emit("filters", filters.value);
}
</script>
