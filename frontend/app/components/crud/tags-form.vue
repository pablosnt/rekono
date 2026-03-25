<template>
  <div>
    <UInput
      class="w-full"
      :placeholder="placeholder"
      :icon="icon"
      :size="size"
      :disabled="disabled"
      @keydown.enter.prevent="addTag"
    />
    <div v-if="modelValue.length" class="flex flex-wrap gap-2 mt-2">
      <UBadge
        v-for="(tag, index) in modelValue"
        :key="index"
        color="neutral"
        variant="subtle"
      >
        {{ tag }}
        <UButton
          icon="i-lucide-x"
          size="xs"
          color="neutral"
          variant="ghost"
          class="ml-1 -mr-1"
          @click="removeTag(index)"
        />
      </UBadge>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue: string[];
    placeholder?: string;
    icon?: string;
    size?: string;
    disabled?: boolean;
  }>(),
  {
    placeholder: "Type and press Enter to add tag",
    icon: undefined,
    size: "lg",
    disabled: false,
  },
);
const emit = defineEmits<{
  "update:modelValue": [value: string[]];
}>();
const validation = useValidation();

function addTag(e: Event) {
  const target = e.target as HTMLInputElement;
  const val = target.value.trim();
  const result = validation.name("tag", false, 100).safeParse(val);
  if (val && !props.modelValue.includes(val) && result.success) {
    emit("update:modelValue", [...props.modelValue, val]);
    target.value = "";
  }
}

function removeTag(index: number) {
  const updated = [...props.modelValue];
  updated.splice(index, 1);
  emit("update:modelValue", updated);
}
</script>
