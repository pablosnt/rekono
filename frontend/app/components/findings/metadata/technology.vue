<template>
  <div v-if="technology" class="flex items-center gap-2 flex-wrap">
    <span class="text-muted">Technology:</span>
    <NuxtLink
      class="flex items-center gap-2 hover:text-primary hover:underline"
      :to="`/projects/${$route.params.project_id}/technologies/${technology.id}`"
    >
      <span class="text-base">{{ technology.name }}</span>
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import type { Technology } from "~/types/models";

defineProps<{ technology: Technology }>();
</script>
