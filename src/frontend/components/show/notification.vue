<template>
  <v-card :title="title" :subtitle="subtitle" class="mx-auto" elevation="4">
    <template #prepend>
      <v-icon size="x-large" :icon="icon" :color="iconColor" />
    </template>
    <template #append>
      <ButtonGreenCheck
        v-if="!loading"
        :condition="data?.is_available"
        true-text="Available"
        false-text="Not available"
      />
      <v-progress-circular
        v-if="loading"
        class="ma-3"
        :color="loadingColor"
        :size="24"
        indeterminate
      />
      <ButtonLink v-if="link" :link="link" />
    </template>
    <v-card-text>
      <v-slot name="prepend" />
      <component
        :is="form"
        :api="api"
        :data="data"
        @completed="(value) => (data = value)"
        @loading="(value) => (loading = value)"
      />
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
const props = defineProps({
  api: Object,
  notification: Object,
  title: String,
  subtitle: {
    type: String,
    required: false,
    default: undefined,
  },
  icon: String,
  iconColor: {
    type: String,
    required: false,
    default: undefined,
  },
  loadingColor: String,
  link: {
    type: String,
    required: false,
    default: undefined,
  },
  form: Object,
});
const data = ref(props.notification);
const loading = ref(false);
</script>
