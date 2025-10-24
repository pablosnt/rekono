<template>
  <v-progress-linear
    v-if="total > 1"
    v-model="percentage"
    height="20"
    color="red"
  >
    <strong>{{ percentage }}%</strong>
  </v-progress-linear>
</template>

<script setup lang="ts">
const props = defineProps({ total: Number, progress: Number });
const percentage = computed(() => {
  return props.total === 0 ? 0 : Math.ceil(props.progress / props.total) * 100;
});
</script>
