<template>
  <MenuProject>
    <TabTarget>
      <HttpHeaderShow :target="route.params.target_id" />
    </TabTarget>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
</script>
