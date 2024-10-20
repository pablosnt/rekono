<template>
  <MenuProject>
    <FindingPage :page="FindingPageFindings" match-query />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const FindingPageFindings = resolveComponent("FindingPageFindings");
</script>
