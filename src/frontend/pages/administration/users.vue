<template>
  <MenuAdministration>
    <UserShow change-role enable-disable />
  </MenuAdministration>
</template>
<!-- TODO: require SMTP to be configured before any invitation. Otherwise there could be a user invited, without email, who can't be removed, who can't receive any other email -->
<!-- TODO: resend invitation feature to prevent situations like this -->
<script setup lang="ts">
definePageMeta({ layout: false });
</script>
