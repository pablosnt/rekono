<template>
  <div v-if="host" class="flex items-center gap-2 flex-wrap">
    <span class="text-muted">Host:</span>
    <NuxtLink
      class="flex items-center gap-2 hover:text-primary hover:underline"
      :to="`/projects/${$route.params.project_id}/hosts/${host.id}`"
    >
      <UIcon
        :name="osConfig?.icon || 'i-lucide-server'"
        :class="`text-${osConfig?.color || 'neutral'}`"
        :aria-label="host.domain || host.ip"
      />
      <span class="text-base">{{ host.domain || host.ip }}</span>
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { hostOS } from "~/constants";
import type { Host } from "~/types/models";

const props = defineProps<{ host: Host }>();
const osConfig = hostOS.find((o) => o.value === props.host?.os_type);
</script>
