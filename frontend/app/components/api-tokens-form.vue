<template>
  <UAlert
    v-if="newToken"
    color="success"
    variant="subtle"
    title="Copy your new API Token"
    :description="newToken.key"
    orientation="horizontal"
  >
    <template #actions>
      <UButton
        icon="i-lucide-copy"
        color="neutral"
        variant="ghost"
        size="lg"
        @click="copyText(newToken.key, 'Token copied to clipboard')"
      />
    </template>
  </UAlert>
  <CrudForm
    v-else
    ref="form"
    :api="api"
    :config="config"
    @submit="
      (data) => {
        newToken = data;
        $emit('new-submit-label', 'Continue');
        $emit('new-loading', false);
      }
    "
    @validation-change="(isValid) => $emit('validation-change', isValid)"
    @new-loading="(newLoading) => $emit('new-loading', newLoading)"
    @error="(error) => $emit('error', error)"
  />
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";

defineProps<{
  api: typeof useApi;
  config: CrudConfig;
}>();
const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
  "validation-change": [isValid: boolean];
  "new-submit-label": [newSubmitLabel: string];
  "new-loading": [newLoading: boolean];
  error: [error: object];
}>();
const form = ref();
const newToken = ref();

function submit() {
  if (!newToken.value) {
    form.value.submit();
  } else {
    emit("submit", newToken.value);
  }
}

defineExpose({ submit });
</script>
