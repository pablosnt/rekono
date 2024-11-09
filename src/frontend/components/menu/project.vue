<template>
  <Menu
    :options="[
      {
        title: 'Dashboard',
        icon: 'mdi-chart-box',
        to: `/projects/${route.params.project_id}/dashboard`,
      },
      {
        title: 'Targets',
        icon: 'mdi-target',
        to: `/projects/${route.params.project_id}/targets`,
      },
      {
        title: 'Scans',
        icon: 'mdi-play-network',
        to: `/projects/${route.params.project_id}/scans`,
      },
      {
        title: 'Assets',
        icon: 'mdi-server',
        to: `/projects/${route.params.project_id}/assets`,
      },
      {
        title: 'Findings',
        icon: 'mdi-ladybug',
        to: `/projects/${route.params.project_id}/findings`,
      },
      {
        title: 'Reports',
        icon: 'mdi-file-document-multiple',
        to: `/projects/${route.params.project_id}/reports`,
      },
      {
        title: 'Alerts',
        icon: 'mdi-alert',
        to: `/projects/${route.params.project_id}/alerts`,
      },
      {
        title: 'Notes',
        icon: 'mdi-notebook',
        to: `/projects/${route.params.project_id}/notes`,
      },
      {
        title: 'Members',
        icon: 'mdi-account-group',
        to: `/projects/${route.params.project_id}/members`,
      },
    ]"
  >
    <slot />
  </Menu>
</template>

<script setup lang="ts">
// TODO: Limit the links available for each user role
const route = useRoute();
</script>
