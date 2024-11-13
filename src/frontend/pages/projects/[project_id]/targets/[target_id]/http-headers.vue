<template>
  <MenuProject>
    <TargetTab>
      <HttpHeader :target="route.params.target_id" />
    </TargetTab>
  </MenuProject>
</template>
<!-- TODO: review the width of this kind of pages, which is different compared with other pages on the same menu -->
<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
</script>
