<template>
  <v-chip
    v-if="value > 0 || showZero"
    :prepend-icon="icon"
    :color="color"
    link
    :to="link"
    @click.prevent.stop
  >
    {{ value < 1000 ? value : Math.floor(value / 1000).toString() + "k" }}
    {{ entity }}
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
  entity: String,
  icon: String,
  color: {
    type: String,
    required: false,
    default: "red",
  },
  link: {
    type: String,
    required: false,
    default: undefined,
  },
  showZero: {
    type: Boolean,
    required: false,
    default: false,
  },
});

const value = ref(props.collection ? props.collection.length : props.number);
</script>
