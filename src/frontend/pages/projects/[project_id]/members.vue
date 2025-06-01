<template>
  <MenuProject>
    <User :project="route.params.project_id" handle-member />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
</script>
