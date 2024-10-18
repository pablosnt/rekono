<template>
  <v-btn
    v-if="entity === null && (value > 0 || showZero)"
    class="mr-4 text-none"
    :icon="icon !== undefined || image !== undefined"
    variant="text"
    :to="link"
    :hover="link !== null"
    :target="newTab ? '_blank' : '_self'"
    stacked
  >
    <v-badge  :content="display">
      <v-avatar
        v-if="size === undefined"
        :icon="icon"
        :image="image"
        :color="color"
        :variant="variant"
      />
      <v-icon v-if="size !== undefined" :icon="icon" :size="size" :color="color"
        
        :variant="variant"/>
    </v-badge>
    <v-tooltip v-if="tooltip !== null" activator="parent" :text="tooltip" />
  </v-btn>
  <v-chip
    v-if="entity !== null && (value > 0 || showZero)"
    class="mr-4"
    :prepend-icon="icon"
    :color="color"
    :link="link !== null"
    :target="newTab ? '_blank' : '_self'"
    @click.stop
  >
    {{ display }} {{ entity }}
  </v-chip>
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
const value = ref(props.collection ? props.collection.length : props.number);
const display =
  value.value < 1000
    ? value.value
    : Math.floor(value.value / 1000).toString() + "k";
</script>
