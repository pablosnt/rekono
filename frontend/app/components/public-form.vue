<template>
  <UAuthForm
    :schema="schema"
    :title="title"
    :description="description"
    :fields="fields"
    :validate-on="validateOn"
    :submit="submit"
    :loading="loading"
    loading-auto
    @submit="
      (data) => {
        $emit('submit', data);
      }
    "
  >
    <template #leading>
      <div class="flex flex-col items-center justify-center mb-3 mt-3">
        <UColorModeImage
          light="/favicon.ico"
          dark="/favicon.ico"
          :width="100"
          :height="100"
        />
      </div>
    </template>
    <template #password-hint>
      <slot name="password-hint" />
    </template>
  </UAuthForm>
</template>

<script setup lang="ts">
import type * as z from "zod";

const props = withDefaults(
  defineProps<{
    title: string;
    description?: string;
    fields: object[];
    schema: z.ZodObject;
    validateOn?: string[];
    submit?: object;
    loading?: boolean;
    maxWidth?: string;
  }>(),
  {
    description: undefined,
    validateOn: ["input", "change"],
    submit: { label: "Submit", autoFocus: true, size: "xl" },
    loading: false,
  },
);
const emit = defineEmits<{
  submit: [data: any];
}>();
</script>
