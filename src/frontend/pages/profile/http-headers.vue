<template>
  <MenuProfile>
    <ShowHttpHeaders :user="user.user" />
  </MenuProfile>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const user = userStore();
</script>
