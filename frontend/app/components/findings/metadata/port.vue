<template>
  <div v-if="port" class="flex items-center gap-2 flex-wrap">
    <span class="text-muted">Port:</span>
    <NuxtLink
      class="flex items-center gap-2 hover:text-primary hover:underline"
      :to="`/projects/${$route.params.project_id}/ports/${port.id}`"
    >
      <UIcon
        :name="getPortIcon(port.port, port.service)"
        class="text-xl"
        :aria-label="port.service || port.port"
      />
      <span class="text-base">{{ port.port }}</span>
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import type { Port } from "~/types/models";

defineProps<{ port: Port }>();
</script>
