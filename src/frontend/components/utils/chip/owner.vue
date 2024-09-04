<template>
  <v-chip
    :color="entity[field] ? 'primary' : undefined"
    :variant="
      !entity[field]
        ? undefined
        : entity[field].id === user.user
          ? 'flat'
          : 'tonal'
    "
  >
    <p v-if="entity[field]">
      <v-icon icon="mdi-at" start />
      {{ entity[field].username }}
    </p>
    <p v-if="!entity[field]">Default</p>
  </v-chip>
</template>

<script setup lang="ts">
defineProps({
  entity: Object,
  field: { type: String, required: false, default: "owner" },
});
const user = userStore();
</script>
