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
const props = defineProps<{
  taskId?: string | number;
  projectId?: string | number;
}>();

const api = useApi("/api/");
const total = ref(0);
const loading = ref(false);
const counters = ref([
  {
    label: "OSINT",
    icon: "i-lucide-rss",
    iconClass: "text-primary",
    iconBgClass: "bg-primary/10",
    accentClass: "bg-primary",
    count: 0,
    loading: false,
  },
  {
    label: "Hosts",
    icon: "i-lucide-server",
    iconClass: "text-slate-500 dark:text-slate-400",
    iconBgClass: "bg-slate-500/10",
    accentClass: "bg-slate-500",
    count: 0,
    loading: false,
  },
  {
    label: "Ports",
    icon: "i-lucide-ethernet-port",
    iconClass: "text-cyan-500",
    iconBgClass: "bg-cyan-500/10",
    accentClass: "bg-cyan-500",
    count: 0,
    loading: false,
  },
  {
    label: "Paths",
    icon: "i-lucide-slash",
    iconClass: "text-teal-500",
    iconBgClass: "bg-teal-500/10",
    accentClass: "bg-teal-500",
    count: 0,
    loading: false,
  },
  {
    label: "Technologies",
    icon: "i-lucide-layers",
    iconClass: "text-amber-500",
    iconBgClass: "bg-amber-500/10",
    accentClass: "bg-amber-500",
    count: 0,
    loading: false,
  },
  {
    label: "Credentials",
    icon: "i-lucide-key",
    iconClass: "text-orange-500",
    iconBgClass: "bg-orange-500/10",
    accentClass: "bg-orange-500",
    count: 0,
    loading: false,
  },
  {
    label: "Vulnerabilities",
    icon: "i-lucide-bug",
    iconClass: "text-error",
    iconBgClass: "bg-error/10",
    accentClass: "bg-error",
    count: 0,
    loading: false,
  },
  {
    label: "Exploits",
    icon: "i-lucide-flame",
    iconClass: "text-rose-600",
    iconBgClass: "bg-rose-600/10",
    accentClass: "bg-rose-600",
    count: 0,
    loading: false,
  },
]);

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
