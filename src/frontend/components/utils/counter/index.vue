<template>
  <component
    :is="UtilsComponent"
    v-if="value > 0 || showZero"
    :value="value"
    :display="display"
    :icon="icon"
    :image="image"
    :size="size"
    :variant="variant"
    :color="color"
    :link="link"
    :show-zero="showZero"
    :new-tab="newTab"
    :tooltip="tooltip"
    :entity="entity"
  />
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
  link: {
    type: String,
    required: false,
    default: null,
  },
  showZero: {
    type: Boolean,
    required: false,
    default: false,
  },
  newTab: {
    type: Boolean,
    required: false,
    default: false,
  },
  entity: {
    type: String,
    required: false,
    default: null,
  },
  tooltip: {
    type: String,
    required: false,
    default: null,
  },
});
const UtilsComponent =
  props.entity !== null
    ? resolveComponent("UtilsCounterChip")
    : resolveComponent("UtilsCounterButton");
const value = ref(props.collection ? props.collection.length : props.number);
const display =
  value.value < 1000
    ? value.value
    : Math.floor(value.value / 1000).toString() + "k";
</script>
