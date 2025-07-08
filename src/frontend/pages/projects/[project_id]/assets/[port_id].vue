<template>
  <MenuProject>
    <FindingPage :page="FindingPortPage" match-query asset />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const FindingPortPage = resolveComponent("FindingPortPage");
</script>
