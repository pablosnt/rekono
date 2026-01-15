<template>
  <div class="space-y-4 mx-auto mt-3">
    <UFormField required name="intensity">
      <USlider
        v-model="intensity"
        class="mt-8 mb-2"
        :min="minIntensity"
        :max="maxIntensity"
        :tooltip="{
          text: utils.intensityOptions[intensity - 1].label,
          open: true,
          content: {
            side: 'top',
            sideOffset: 8,
            collisionPadding: 8,
          },
        }"
        :color="utils.intensityOptions[intensity - 1]?.color"
        @update:model-value="$emit('update-intensity', intensity)"
      />
      <UAlert
        v-if="isProcessSelected && intensity < 5"
        class="mt-10"
        icon="i-lucide-zap"
        color="warning"
        title="Steps that only support higher intensities won't be executed"
        variant="subtle"
      />
    </UFormField>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  minIntensity: number;
  maxIntensity: number;
  isProcessSelected: boolean;
}>();
defineEmits<{
  "update-intensity": [newIntensity: number];
}>();

const utils = useUtils();
const intensity = ref(3);

watch(
  () => props.maxIntensity,
  () => (intensity.value = props.maxIntensity >= 3 ? 3 : props.maxIntensity),
);
</script>
