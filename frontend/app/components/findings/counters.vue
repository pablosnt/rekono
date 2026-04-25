<template>
  <div
    v-if="total > 0 || loading"
    class="grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-8 gap-3"
  >
    <NuxtLink
      v-for="item in counters"
      :key="item.label"
      :to="`/projects/${projectId}/${item.label.toLowerCase()}${taskId ? `?task=${taskId}` : ''}`"
      color="primary"
      class="group relative flex flex-col items-center gap-1.5 p-3 rounded-xl border border-default bg-elevated hover:bg-muted/50 hover:border-default/80 transition-all duration-200 text-center overflow-hidden"
    >
      <div
        v-if="item.count > 0"
        :class="['absolute top-0 inset-x-0 h-0.5', item.accentClass]"
      />
      <div
        :class="[
          'size-8 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-200',
          item.iconBgClass,
        ]"
      >
        <UIcon :name="item.icon" :class="['size-4', item.iconClass]" />
      </div>
      <div class="leading-none">
        <USkeleton
          v-if="item.loading && item.count === 0"
          class="h-6 w-10 mx-auto mt-0.5"
        />
        <span
          v-else
          :class="[
            'text-xl font-bold font-mono tracking-tight text-highlighted',
            item.count === 0 ? 'text-muted' : undefined,
          ]"
        >
          {{ item.count.toLocaleString() }}
        </span>
      </div>
      <span class="text-[11px] leading-tight text-muted font-medium">{{
        item.label
      }}</span>
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { findingTypes } from '~/constants';

const props = defineProps<{
  taskId?: string | number;
  projectId?: string | number;
}>();

const api = useApi("/api/");
const total = ref(0);
const loading = ref(false);
const counters = ref(findingTypes.map((ft) => {
  const color = ['primary', 'error'].includes(ft.color) ? ft.color : `${ft.color}-${ft.color === 'rose' ? '600' : '500'}`
  const iconClass = ft.color === 'slate' ? "text-slate-500 dark:text-slate-400" : `text-${color}`
  return {
    label: ft.plural,
    icon: ft.icon,
    iconClass: iconClass,
    iconBgClass: `bg-${color}/10`,
    accentClass: `bg-${color}`,
    count: 0,
    loading: false
  }
}))

function fetch() {
  total.value = 0;
  loading.value = true;
  counters.value.forEach((c) => {
    c.loading = true;
  });
  counters.value.forEach((counter, index) => {
    api
      .list(
        `${counter.label.toLowerCase()}/`,
        props.taskId
          ? { task: props.taskId }
          : props.projectId
            ? { project: props.projectId }
            : {},
        false,
        1,
        1,
      )
      .then((response: { items: unknown[]; total: number }) => {
        counters.value[index].count = response.total;
        total.value += response.total;
      })
      .catch(() => {
        counters.value[index].count = 0;
      })
      .finally(() => {
        counters.value[index].loading = false;
        loading.value = counters.value.some((c) => c.loading);
      });
  });
}

onMounted(fetch);

defineExpose({ fetch });
</script>
