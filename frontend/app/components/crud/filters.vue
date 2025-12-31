<template>
  <div class="border-b border-default bg-muted/30 p-4 space-y-4">
    <div class="flex flex-wrap gap-4 justify-around">
      <template v-for="filter in config.filters" :key="filter.key">
        <USelectMenu
          v-if="filter.type === 'select'"
          :model-value="_filters[filter.key]"
          :placeholder="filter.placeholder || filter.label"
          :items="Array.isArray(filter.options) ? filter.options : []"
          value-key="value"
          label-key="label"
          class="w-64"
          :avatar="
            (Array.isArray(filter.options)
              ? filter.options.filter(
                  (option: FilterOption) =>
                    option.value === _filters[filter.key],
                )?.[0]?.avatar
              : undefined) || filter.avatar
          "
          :icon="
            (Array.isArray(filter.options)
              ? filter.options.filter(
                  (option: FilterOption) =>
                    option.value === _filters[filter.key],
                )?.[0]?.icon
              : undefined) || filter.icon
          "
          leading
          @update:model-value="(value) => updateFilter(filter.key, value)"
        >
          <template #trailing>
            <UIcon
              v-if="
                _filters[filter.key] === null ||
                _filters[filter.key] === undefined
              "
              class="group-data-[state=open]:rotate-180 transition-transform duration-200"
              name="i-lucide-chevron-down"
            />
            <UButton
              v-else
              icon="i-lucide-x"
              variant="ghost"
              color="neutral"
              size="sm"
              @click="updateFilter(filter.key, null)"
            />
          </template>
        </USelectMenu>
        <UInput
          v-else-if="filter.type === 'text'"
          :model-value="_filters[filter.key] as string"
          :placeholder="filter.placeholder || filter.label"
          :icon="filter.icon"
          class="w-64"
          @update:model-value="(value) => updateFilter(filter.key, value)"
        />
        <UCheckbox
          v-else-if="filter.type === 'boolean'"
          :model-value="
            (filter.value
              ? _filters[filter.key] === filter.value
              : _filters[filter.key]) as boolean
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
import type { CrudConfig, CrudState } from "~/types/crud";

const props = defineProps<{
  config: CrudConfig;
  state: CrudState;
}>();
const emit = defineEmits<{
  filters: [filters: Record<string, unknown>];
}>();
const _filters = ref(props.state.filters);

function updateFilter(key: string, value: unknown) {
  if (value !== null && value !== undefined && value !== "") {
    _filters.value[key] = value;
  } else {
    delete _filters.value[key];
  }
  emit("filters", _filters.value);
}
</script>
