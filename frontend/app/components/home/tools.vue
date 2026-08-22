<template>
  <UPageSection title="Supported Tools">
    <ul class="sr-only">
      <li v-for="tool in tools" :key="tool.id">{{ tool.name }}</li>
    </ul>
    <UMarquee
      aria-hidden="true"
      pause-on-hover
      :ui="{ content: 'will-change-transform' }"
    >
      <div
        v-for="tool in tools"
        :key="tool.id"
        class="flex flex-col items-center gap-2"
      >
        <UAvatar :src="tool.icon" :alt="tool.name" size="xl" />
        <span>{{ tool.name }}</span>
      </div>
    </UMarquee>
  </UPageSection>
</template>

<script setup lang="ts">
import type { Tool } from "~/types/models";

defineProps<{ tools: Tool[] }>();
</script>
