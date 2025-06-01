<template>
  <MenuProject>
    <TargetTabs>
      <HttpHeader :target="route.params.target_id" />
    </TargetTabs>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
</script>
