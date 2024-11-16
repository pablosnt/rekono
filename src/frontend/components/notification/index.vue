<template>
  <v-card :title="title" :subtitle="subtitle" class="mx-auto" elevation="2">
    <template #prepend>
      <v-icon
        size="x-large"
        :icon="enums.notificationPlatforms[title].icon"
        :color="enums.notificationPlatforms[title].color"
      />
    </template>
    <template #append>
      <UtilsGreenCheck
        v-if="!loading"
        :condition="data?.is_available"
        true-text="Available"
        false-text="Not available"
      />
      <v-progress-circular
        v-if="loading"
        class="ma-3"
        :color="enums.notificationPlatforms[title].color"
        :size="24"
        indeterminate
      />
      <BaseButton :link="link" new-tab hide />
    </template>
    <v-card-text>
      <component
        :is="form"
        :api="api"
        :data="data"
        @completed="
          (value) => {
            $emit('completed', value);
            data = value;
          }
        "
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
  link: {
    type: String,
    required: false,
    default: undefined,
  },
  form: Object,
});
defineEmits(["completed"]);
const enums = useEnums();
const data = ref(props.notification);
const loading = ref(false);
</script>
