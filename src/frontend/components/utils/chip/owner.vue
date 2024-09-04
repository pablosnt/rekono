<template>
  <v-chip
    :color="entity.owner ? 'primary' : undefined"
    :variant="
      !entity.owner
        ? undefined
        : entity.owner.id === user.user
          ? 'flat'
          : 'tonal'
    "
  >
    <p v-if="entity.owner">
      <v-icon icon="mdi-at" start />
      {{ entity.owner.username }}
    </p>
    <p v-if="!entity.owner">Default</p>
  </v-chip>
</template>

<script setup lang="ts">
defineProps({ entity: Object });
const user = userStore();
</script>
