<template>
  <v-card variant="text" width="100%" :subtitle="subtitle">
    <template #prepend>
      <v-card-title v-if="icon" :class="titleClass">
        <v-icon :color="color" :icon="icon" />
      </v-card-title>
    </template>
    <template #title>
      <v-card-title :class="titleClass">{{ title }}</v-card-title>
    </template>
    <template #text>
      <v-card-text>
        <slot />
      </v-card-text>
    </template>
  </v-card>
</template>

<script setup lang="ts">
defineProps({
  title: String,
  titleClass: {
    type: String,
    required: false,
    default: "text-h5",
  },
  subtitle: {
    type: String,
    required: false,
    default: undefined,
  },
  icon: {
    type: String,
    required: false,
    default: undefined,
  },
  color: {
    type: String,
    required: false,
    default: "red",
  },
});
</script>
