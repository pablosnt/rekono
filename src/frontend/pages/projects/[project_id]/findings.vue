<template>
  <MenuProject>
    <FindingPage :page="FindingPageFindings" match-query triage />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const FindingPageFindings = resolveComponent("FindingPageFindings");
</script>
