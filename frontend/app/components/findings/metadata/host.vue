<template>
  <div v-if="host" class="flex items-center gap-2 flex-wrap">
    <span class="text-muted">Host:</span>
    <a
      class="flex items-center gap-2 hover:text-primary hover:underline"
      :href="`/projects/${$route.params.project_id}/hosts/${host.id}`"
    >
      <UIcon
        :name="osConfig?.icon || 'i-lucide-server'"
        :class="`text-${osConfig?.color || 'neutral'}`"
      />
      <span class="text-base">{{ host.domain || host.ip }}</span>
    </a>
  </div>
</template>

<script setup lang="ts">
import { hostOS } from "~/constants";
import type { Host } from "~/types/models";

const props = defineProps<{ host: Host }>();
const osConfig = hostOS.find((o) => o.value === props.host.os_type);
</script>
