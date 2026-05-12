<template>
  <NuxtLink
    :to="
      projectId
        ? `/projects/${projectId}/${counter.plural.toLowerCase()}${taskId ? `?task=${taskId}` : ''}`
        : `/${counter.plural.toLowerCase()}`
    "
    :aria-label="`${formatCount(counter.count as number)} ${counter.plural}`"
    color="primary"
    class="group relative flex flex-col items-center justify-center gap-1.5 p-3 rounded-xl border border-default bg-elevated hover:bg-muted/50 hover:border-default/80 transition-all duration-200 text-center overflow-hidden"
  >
    <div
      v-if="counter.count > 0"
      :class="['absolute top-0 inset-x-0 h-0.5', counter.accentClass]"
    />
    <div
      :class="[
        'size-8 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-200',
        counter.iconBgClass,
      ]"
    >
      <UIcon :name="counter.icon" :class="['size-4', counter.iconClass]" />
    </div>
    <div class="leading-none">
      <USkeleton
        v-if="counter.loading && counter.count === 0"
        class="h-6 w-10 mx-auto mt-0.5"
      />
      <span
        v-else
        :class="[
          'text-xl font-bold font-mono tracking-tight text-highlighted',
          counter.count === 0 ? 'text-muted' : undefined,
        ]"
      >
        {{ formatCount(counter.count as number) }}
      </span>
    </div>
    <span class="text-[11px] leading-tight text-muted font-medium">{{
      counter.plural
    }}</span>
  </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{
  taskId?: string | number;
  projectId?: string | number;
  counter: Record<string, string | number>;
}>();
</script>
