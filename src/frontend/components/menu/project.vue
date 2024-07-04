<template>
  <Menu
    :options="[
      { title: 'Dashboard', icon: 'mdi-chart-box', to: `/projects/${project}` },
      {
        title: 'Targets',
        icon: 'mdi-target',
        to: `/projects/${project}/targets`,
      },
      {
        title: 'Scans',
        icon: 'mdi-play-network',
        to: `/projects/${project}/scans`,
      },
      {
        title: 'Findings',
        icon: 'mdi-ladybug',
        to: `/projects/${project}/findings`,
      },
      {
        title: 'Reports',
        icon: 'mdi-file-document-multiple',
        to: `/projects/${project}/reports`,
      },
      { title: 'Alerts', icon: 'mdi-alert', to: `/projects/${project}/alerts` },
      {
        title: 'Notes',
        icon: 'mdi-notebook',
        to: `/projects/${project}/notes`,
      },
      {
        title: 'Members',
        icon: 'mdi-account-group',
        to: `/projects/${project}/members`,
      },
    ]"
  >
    <slot />
  </Menu>
</template>

<script setup lang="ts">
const route = useRoute();
const project = ref(route.params.project_id);
</script>
