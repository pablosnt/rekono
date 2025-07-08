<template>
  <MenuProject>
    <FindingPage :page="FindingHostPage" asset />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const FindingHostPage = resolveComponent("FindingHostPage");
</script>
