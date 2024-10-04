<template>
  <v-btn
    v-if="link"
    variant="text"
    icon="mdi-open-in-new"
    color="medium-emphasis"
    target="_blank"
    :href="link"
    hover
  />
</template>

<script setup lang="ts">
defineProps({ link: String });
</script>
