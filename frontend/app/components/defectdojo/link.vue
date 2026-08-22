<template>
  <UButton
    v-if="integrations.defectdojo.settings?.is_available && id"
    :to="`${integrations.defectdojo.settings.server}/${entity}/${id}`"
    target="_blank"
    :avatar="
      icon
        ? undefined
        : { src: integrations.defectdojo.integration?.icon, size: size || 'xl' }
    "
    :icon="icon"
    :aria-label="`Open ${entity} in DefectDojo`"
    variant="ghost"
    color="neutral"
  />
</template>

<script setup lang="ts">
import { useIntegrationsStore } from "~/store/integrations";

defineProps<{ entity: string; id?: number; icon?: string; size?: string }>();

const integrations = useIntegrationsStore();
</script>
