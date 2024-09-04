<template>
  <MenuProject>
    <UserShow :project="route.params.project_id" :handle-member="true" />
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
</script>
