<template>
  <v-card
    class="mx-auto"
    elevation="4"
    :color="color"
    :width="width"
    :loading="loading ? 'red' : false"
    :title="title"
    :prepend-avatar="avatar"
  >
    <template #append>
      <slot name="extra-append" />
      <v-btn icon="mdi-close" variant="text" @click="$emit('closeDialog')" />
    </template>
    <v-card-text class="overflow-auto">
      <slot />
    </v-card-text>
    <slot name="card" />
  </v-card>
</template>

<script setup lang="ts">
defineProps({
  title: String,
  loading: {
    type: Boolean,
    required: false,
    default: false,
  },
  color: {
    type: String,
    required: false,
    default: "default",
  },
  width: {
    type: String,
    required: false,
    default: "800",
  },
  avatar: {
    type: String,
    required: false,
    default: undefined,
  },
});
defineEmits(["closeDialog"]);
</script>
