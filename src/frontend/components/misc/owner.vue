<template>
  <v-chip
    v-if="entity.owner"
    color="primary"
    :variant="entity.owner.id === user.user ? 'flat' : 'tonal'"
  >
    <v-icon icon="mdi-at" start />
    {{ entity.owner.username }}
  </v-chip>
  <v-chip v-if="!entity.owner">Default</v-chip>
</template>

<script setup lang="ts">
defineProps({ entity: Object });
const user = userStore();
</script>
