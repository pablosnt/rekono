<template>
  <MenuProject>
    <FindingPage :page="FindingPagePort" match-query />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const FindingPagePort = resolveComponent("FindingPagePort");
</script>
