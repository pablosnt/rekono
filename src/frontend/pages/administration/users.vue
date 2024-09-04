<template>
  <MenuAdministration>
    <UserShow :change-role="true" :enable-disable="true" />
  </MenuAdministration>
</template>
<!-- todo: require SMTP to be configured before any invitation. Otherwise there could be a user invited, without email, who can't be removed, who can't receive any other email -->
<!-- todo: resend invitation feature to prevent situations like this -->
<script setup lang="ts">
definePageMeta({ layout: false });
</script>
