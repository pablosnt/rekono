<template>
  <UModal
    :open="open"
    :title="
      title || (item ? `Edit ${config.entityName}` : `New ${config.entityName}`)
    "
    :ui="{ content: 'sm:max-w-3xl sm:max-h-xl', footer: 'justify-end' }"
    @update:open="(value: boolean) => $emit('open', value)"
  >
    <template #body>
      <CrudForm
        ref="formRef"
        :api="api"
        :config="config"
        :entity="item"
        @submit="
          $emit('submit');
          $emit('open', false);
        "
      />
    </template>
    <template #footer="{ close }">
      <UButton
        label="Cancel"
        color="neutral"
        variant="outline"
        @click="close"
      />
      <UButton
        color="primary"
        :label="submitLabel || (item ? 'Save' : 'Create')"
        @click="formRef.submit()"
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";

defineProps<{
  open: boolean;
  item?: Record<string, string | number | boolean | null>;
  config: CrudConfig;
  api: object;
  title?: string;
  submitLabel?: string;
}>();

defineEmits<{
  open: [open: boolean];
  submit: [];
}>();

const formRef = ref();
</script>
