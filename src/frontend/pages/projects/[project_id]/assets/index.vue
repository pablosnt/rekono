<template>
  <MenuProject>
    <FindingPage :page="FindingPageAssets" asset />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const FindingPageAssets = resolveComponent("FindingPageAssets");
</script>
