<template>
  <UPageSection
    title="Core Features"
    :features="[
      {
        title: 'Processes',
        description:
          'Design your scanning workflows to combine multiple hacking tools',
        icon: 'i-lucide-workflow',
        to: '/processes',
      },
      {
        title: 'Reports',
        description:
          'Export polished reports in multiple formats, ready for clients, stakeholders, or automated pipelines',
        icon: 'i-lucide-file-text',
        ui: { leadingIcon: 'text-neutral' },
      },
      {
        title: 'Metrics',
        description:
          'Track vulnerability trends, measure coverage, and visualize how your attack surface evolves',
        icon: 'i-lucide-chart-bar',
        to: '/metrics',
        ui: { leadingIcon: 'text-success' },
      },
      {
        title: 'Alerts',
        description:
          'Receive notifications when the finding that you are looking for is detected',
        icon: 'i-lucide-triangle-alert',
        ui: { leadingIcon: 'text-warning' },
      },
      {
        title: 'Notes',
        description:
          'Capture hypotheses, annotate findings, and plan your recon strategy where the work happens',
        icon: 'i-lucide-notebook',
        ui: { leadingIcon: 'text-purple-500' },
      },
      {
        title: 'Telegram Bot',
        description:
          'Away From Keyboard? Keep triggering scans from our Telegram Bot',
        icon: 'i-simple-icons-telegram',
        to: integrationsStore.telegram?.is_available
          ? `https://t.me/${integrationsStore.telegram?.bot}`
          : undefined,
        target: integrationsStore.telegram?.is_available ? '_blank' : undefined,
        ui: { leadingIcon: 'text-info' },
      },
    ]"
  />
</template>

<script setup lang="ts">
import { useIntegrationsStore } from "~/store/integrations";

const integrationsStore = useIntegrationsStore();
</script>
