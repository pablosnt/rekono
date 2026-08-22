<template>
  <div class="flex flex-wrap items-center gap-2">
    <UBadge
      v-for="filter in filters"
      :key="filter.key"
      color="neutral"
      variant="outline"
      size="lg"
      :icon="filter.icon"
      :label="`${loaded[filter.key]?.label ?? `#${filter.value}`}`"
    >
      <template #trailing>
        <UButton
          icon="i-lucide-x"
          variant="ghost"
          color="neutral"
          size="xs"
          :aria-label="`Clear ${filter.label} filter`"
          @click="emit('clear', filter.key)"
        />
      </template>
    </UBadge>
  </div>
</template>

<script setup lang="ts">
import type { AcceptedFilterConfig, FilterOption } from "~/types/crud";

const props = defineProps<{
  filters: (AcceptedFilterConfig & { value: string | number })[];
}>();
const emit = defineEmits<{ clear: [key: string] }>();

const loaded = reactive<Record<string, FilterOption>>({});

props.filters.forEach((filter) => {
  filter
    .loadOption(filter.value)
    .then((option) => {
      loaded[filter.key] = option;
    })
    .catch(() => {});
});
</script>
