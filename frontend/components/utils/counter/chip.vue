<template>
  <v-chip
    v-if="value > 0 || showZero"
    class="mr-4"
    :prepend-icon="icon"
    :color="color"
    :to="link"
    :link="link !== null"
    :target="newTab ? '_blank' : '_self'"
    :variant="variant"
    @click.prevent.stop
  >
    {{ utils.displayNumber(collection ? collection.length : number) }}
    {{ entity }}
  </v-chip>
</template>

<script setup lang="ts">
const props = defineProps({
  number: { type: Number, required: false, default: 0 },
  collection: { type: Array, required: false, default: null },
  variant: { type: String, required: false, default: "tonal" },
  color: { type: String, required: false, default: "red" },
  link: { type: String, required: false, default: null },
  newTab: { type: Boolean, required: false, default: false },
  entity: String,
  showZero: { type: Boolean, required: false, default: false },
});
const utils = useUtils();
const value = ref(props.collection ? props.collection.length : props.number);
</script>
