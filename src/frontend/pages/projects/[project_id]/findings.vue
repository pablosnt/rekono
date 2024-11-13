<template>
  <MenuProject>
    <FindingPage :page="FindingOsintVulnerabilityPage" match-query />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const FindingOsintVulnerabilityPage = resolveComponent(
  "FindingOsintVulnerabilityPage",
);
</script>
