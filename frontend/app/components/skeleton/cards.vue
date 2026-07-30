<template>
  <UPageGrid aria-hidden="true">
    <UPageCard
      v-for="card in count"
      :key="card"
      :variant="variant"
      :ui="{ body: 'w-full' }"
    >
      <template v-if="leading" #leading>
        <USkeleton class="size-5" />
      </template>
      <template #title>
        <USkeleton class="h-6 w-28" />
      </template>
      <template #description>
        <slot name="description" :card="card">
          <div v-if="lines > 0" class="space-y-2">
            <USkeleton
              v-for="line in lines"
              :key="line"
              :class="['h-4', line === lines ? 'w-2/3' : 'w-full']"
            />
          </div>
        </slot>
      </template>
      <div
        v-if="actions > 0"
        class="absolute top-4 right-4 flex items-center gap-3"
      >
        <USkeleton v-for="action in actions" :key="action" class="size-8" />
      </div>
      <slot :card="card" />
    </UPageCard>
  </UPageGrid>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    count?: number;
    lines?: number;
    actions?: number;
    variant?: string;
    leading?: boolean;
  }>(),
  { count: 6, lines: 2, actions: 0, variant: "subtle", leading: true },
);
</script>
