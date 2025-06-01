<template>
  <v-card variant="text" width="100%" :subtitle="subtitle" :loading="loading">
    <template #prepend>
      <slot name="prepend">
        <v-card-title v-if="icon" :class="titleClass">
          <v-icon :color="color" :icon="icon" />
        </v-card-title>
      </slot>
    </template>
    <template #title>
      <v-card-title :class="titleClass">{{ title }}</v-card-title>
    </template>
    <template #append>
      <slot name="append" />
    </template>
    <template #text>
      <v-card-text v-if="!notWrappedText">
        <slot />
      </v-card-text>
      <slot v-if="notWrappedText" />
    </template>
  </v-card>
</template>

<script setup lang="ts">
defineProps({
  title: String,
  titleClass: { type: String, required: false, default: "text-h5" },
  subtitle: { type: String, required: false, default: undefined },
  icon: { type: String, required: false, default: undefined },
  color: { type: String, required: false, default: "red" },
  loading: { type: String, required: false, default: undefined },
  notWrappedText: { type: Boolean, required: false, default: false },
});
</script>
