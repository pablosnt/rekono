<template>
  <v-card
    class="mx-auto"
    :elevation="elevation"
    :color="color"
    :width="width"
    :loading="loading ? 'red' : false"
    :title="title"
    :subtitle="subtitle"
    :prepend-avatar="avatar ? avatar : undefined"
    :prepend-icon="!iconColor ? icon : undefined"
    :variant="variant"
  >
    <template v-if="icon && iconColor" #prepend>
      <v-icon :icon="icon" :color="iconColor" />
    </template>
    <template #append>
      <slot name="append" />
      <BaseButton icon="mdi-close" @click="$emit('closeDialog')" />
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
  subtitle: {
    type: String,
    required: false,
    default: undefined,
  },
  avatar: {
    type: String,
    required: false,
    default: undefined,
  },
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
  icon: {
    type: String,
    required: false,
    default: undefined,
  },
  iconColor: {
    type: String,
    required: false,
    default: undefined,
  },
  elevation: {
    type: String,
    required: false,
    default: "3",
  },
});
defineEmits(["closeDialog"]);
</script>
