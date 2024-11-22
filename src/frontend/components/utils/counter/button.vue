<template>
  <BaseButton
    v-if="value > 0 || showZero"
    class="mr-4 text-none"
    :icon="icon !== undefined || image !== undefined"
    stacked
  >
    <template #icon>
      <v-badge :content="utils.displayNumber(value)">
        <v-avatar
          v-if="size === undefined"
          :icon="icon"
          :image="image"
          :color="color"
          :variant="variant"
        />
        <v-icon
          v-if="size !== undefined"
          :icon="icon"
          :size="size"
          :color="color"
          :variant="variant"
        />
      </v-badge>
    </template>
  </BaseButton>
</template>

<script setup lang="ts">
const props = defineProps({
  number: {
    type: Number,
    required: false,
    default: 0,
  },
  collection: {
    type: Array,
    required: false,
    default: null,
  },
  icon: {
    type: String,
    required: false,
    default: undefined,
  },
  image: {
    type: String,
    required: false,
    default: undefined,
  },
  size: {
    type: String,
    required: false,
    default: undefined,
  },
  variant: {
    type: String,
    required: false,
    default: "tonal",
  },
  color: {
    type: String,
    required: false,
    default: "red",
  },
  showZero: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const utils = useUtils();
const value = ref(props.collection ? props.collection.length : props.number);
</script>
