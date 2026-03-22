<template>
  <div class="border-b border-default bg-muted/30 p-4 space-y-4">
    <div class="flex flex-wrap gap-4 justify-around">
      <template v-for="filter in config.filters" :key="filter.key">
        <USelectMenu
          v-if="filter.type === 'select'"
          :model-value="_filters[filter.key]"
          :placeholder="filter.placeholder || filter.label"
          :items="Array.isArray(filter.options) ? filter.options : []"
          :value-key="filter.valueKey || 'value'"
          :label-key="filter.labelKey || 'label'"
          class="w-64"
          :avatar="getSelectConfig(filter)?.avatar"
          :icon="
            getSelectConfig(filter)?.avatar
              ? undefined
              : getSelectConfig(filter)?.icon
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
          v-else-if="filter.type === 'checkbox'"
          :model-value="
            (filter.value
              ? _filters[filter.key] === filter.value
              : _filters[filter.key]) as boolean
          "
          :label="filter.label"
          :icon="filter.icon"
          class="w-32 items-center"
          @update:model-value="
            (value) =>
              updateFilter(
                filter.key,
                filter.value ? (value === true ? filter.value : null) : value,
              )
          "
        />
        <UFormField
          v-else-if="filter.type === 'range'"
          :label="filter.label"
          class="w-64"
        >
          <USlider
            :model-value="
              filter.multiple
                ? [
                    _filters[`${filter.key}__gte`] || filter.min || 0,
                    _filters[`${filter.key}__lte`] || filter.max || 100,
                  ]
                : _filters[filter.key]
            "
            :min="filter.min || 0"
            :max="filter.max || 100"
            :step="filter.step || 1"
            :multiple="filter.multiple || false"
            :tooltip="{ open: true }"
            @update:model-value="
              (value) => {
                if (filter.multiple) {
                  const isValueValid =
                    value && Array.isArray(value) && value.length > 0;
                  updateFilter(
                    `${filter.key}__gte`,
                    isValueValid ? Math.min.apply(Math, value) : undefined,
                    isValueValid ? 300 : undefined,
                  );
                  updateFilter(
                    `${filter.key}__lte`,
                    isValueValid ? Math.max.apply(Math, value) : undefined,
                    isValueValid ? 300 : undefined,
                  );
                } else {
                  updateFilter(filter.key, value);
                }
              }
            "
          />
        </UFormField>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig, CrudState, FilterConfig } from "~/types/crud";

const props = defineProps<{
  config: CrudConfig;
  state: CrudState;
}>();
const emit = defineEmits<{
  filters: [filters: Record<string, unknown>];
}>();
const _filters = ref(props.state.filters);
const updating = [];
let delayTimeout: NodeJS.Timeout | null = null;

function getSelectConfig(filter: FilterConfig) {
  return _filters.value[filter.key]
    ? filter.options.find(
        (option: FilterOption) =>
          (filter.valueKey ? option[filter.valueKey] : option.value) ===
          _filters.value[filter.key],
      )
    : filter;
}

function updateFilter(
  key: string,
  value: unknown,
  delay: number | undefined = undefined,
) {
  if (props.config.defaultFilters && key in props.config.defaultFilters) return;
  updating.push(key);
  if (value !== null && value !== undefined && value !== "") {
    _filters.value[key] = value;
  } else {
    delete _filters.value[key];
  }
  updating.splice(updating.indexOf(key));
  if (delay) {
    if (delayTimeout) {
      clearTimeout(delayTimeout);
    }
    delayTimeout = setTimeout(() => {
      if (updating.includes(key)) return;
      emit("filters", _filters.value);
    }, delay);
  } else {
    emit("filters", _filters.value);
  }
}
</script>
