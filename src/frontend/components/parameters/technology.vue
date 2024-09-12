<template>
  <v-card
    title="Vulnerabilities"
    :prepend-icon="enums.findings.Vulnerability.icon"
    variant="text"
  >
    <!-- TODO -->
  </v-card>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const enums = useEnums();
</script>
