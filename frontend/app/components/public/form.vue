<template>
  <div>
    <UAuthForm
      :schema="schema"
      :title="title"
      :description="description"
      :fields="fields"
      :validate-on="validateOn"
      :submit="{ name: 'submit', ...submit }"
      :loading="loading"
      loading-auto
      :ui="{ otp: 'w-full flex justify-center', description: 'mt-3' }"
      @submit="
        (data) => {
          $emit('submit', data);
        }
      "
    >
      <template #leading>
        <div class="flex flex-col items-center justify-center mb-3 mt-3">
          <UColorModeImage
            light="/favicon-light.png"
            dark="/favicon-dark.png"
            :width="100"
            :height="100"
            alt="Rekono logo"
          />
        </div>
      </template>
      <template #title>
        <h1>{{ title }}</h1>
      </template>
      <template #password-hint>
        <slot name="password-hint" />
      </template>
      <template v-if="$slots.footer" #footer>
        <slot name="footer" />
      </template>
    </UAuthForm>
    <slot name="after-form" />
  </div>
</template>

<script setup lang="ts">
import type * as z from "zod";

withDefaults(
  defineProps<{
    title: string;
    description?: string;
    fields?: object[];
    schema?: z.ZodObject;
    validateOn?: string[];
    submit?: object;
    loading?: boolean;
    maxWidth?: string;
  }>(),
  {
    description: undefined,
    fields: () => [],
    schema: undefined,
    validateOn: () => ["input", "change"],
    submit: () => ({ label: "Submit", autoFocus: true, size: "xl" }),
    loading: false,
  },
);
defineEmits<{
  submit: [data: object];
}>();
</script>
