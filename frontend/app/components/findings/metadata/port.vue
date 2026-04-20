<template>
  <div v-if="port" class="flex items-center gap-2">
    <span class="text-muted">Port:</span>
    <a
      class="flex items-center gap-2 hover:text-primary hover:underline"
      :href="`/projects/${$route.params.project_id}/ports/${port.id}`"
    >
      <UIcon :name="getPortIcon(port.port, port.service)" class="text-xl" />
      <span class="text-base">{{ port.port }}</span>
    </a>
  </div>
</template>

<script setup lang="ts">
import type { Port } from "~/types/models";

defineProps<{ port: Port }>();
</script>
