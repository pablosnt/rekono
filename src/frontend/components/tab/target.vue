<template>
  <Tab
    :options="[
      {
        title: 'Scope',
        icon: 'mdi-antenna',
        to: `/projects/${route.params.project_id}/targets/${route.params.target_id}/scope`,
      },
      {
        title: 'Parameters',
        icon: 'mdi-inbox-arrow-down',
        to: `/projects/${route.params.project_id}/targets/${route.params.target_id}/parameters`,
      },
      {
        title: 'HTTP Headers',
        icon: 'mdi-web',
        to: `/projects/${route.params.project_id}/targets/${route.params.target_id}/http-headers`,
      },
    ]"
  >
    <slot />
  </Tab>
</template>

<script setup lang="ts">
const route = useRoute();
</script>
