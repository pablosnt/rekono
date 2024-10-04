<template>
  <Tab
    :options="[
      {
        title: 'OSINT',
        icon: enums.findings.OSINT.icon,
        to: `/projects/${route.params.project_id}/findings/osint`,
      },
      {
        title: 'Assets',
        icon: enums.findings.Host.icon,
        to: `/projects/${route.params.project_id}/findings/assets`,
      },
      {
        title: 'Vulnerabilities',
        icon: enums.findings.Vulnerability.icon,
        to: `/projects/${route.params.project_id}/findings/vulnerabilities`,
      },
    ]"
  >
    <slot />
  </Tab>
</template>

<script setup lang="ts">
const route = useRoute();
const enums = useEnums();
</script>
