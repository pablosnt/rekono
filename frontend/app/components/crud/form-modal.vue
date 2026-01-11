<template>
  <UModal
    :open="open"
    :title="modalTitle"
    :fullscreen="config.formFullscreen ? true : false"
    :ui="
      ui
        ? ui
        : {
            content: config.formFullscreen ? '' : 'sm:max-w-3xl sm:max-h-xl',
            footer: 'justify-end',
          }
    "
    @update:open="(value: boolean) => $emit('open', value)"
  >
    <template #body>
      <component
        :is="formComponent"
        ref="form"
        :api="api"
        :config="config"
        :entity="item"
        @submit="(data) => handleSubmit(data)"
        @new-title="(newTitle: string) => (updatedTitle = newTitle)"
        @new-submit-label="
          (newSubmitLabel: string) => (updatedSubmitLabel = newSubmitLabel)
        "
        @validation-change="(isValid: boolean) => (formValid = isValid)"
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
        :label="submitButton"
        :disabled="!formValid"
        :loading="loading"
        @click="
          loading = true;
          form?.submit();
        "
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { resolveComponent } from "vue";
import type { CrudConfig } from "~/types/crud";

const props = defineProps<{
  open: boolean;
  item?: Record<string, string | number | boolean | null>;
  config: CrudConfig;
  api: object;
  title?: string;
  submitLabel?: string;
  ui?: Record<string, unknown>;
}>();

const emit = defineEmits<{
  open: [open: boolean];
  submit: [];
}>();

const form = ref();
const formComponent = ref(
  (props.item ? props.config.editForm : props.config.createForm) ||
    resolveComponent("CrudForm"),
);
const updatedTitle = ref();
const modalTitle = computed(
  () =>
    updatedTitle.value ||
    props.title ||
    (props.item
      ? `Edit ${props.config.entityName}`
      : `New ${props.config.entityName}`),
);
const updatedSubmitLabel = ref();
const submitButton = computed(
  () =>
    updatedSubmitLabel.value ||
    props.submitLabel ||
    (props.item ? "Save" : "Create"),
);
const formValid = ref(props.item ? true : false);
const loading = ref(false);

const handleSubmit = (data: Record<string, unknown>) => {
  if (props.config.onCreation) {
    props.config.onCreation(data);
  }
  emit("submit");
  emit("open", false);
  updatedTitle.value = null;
  updatedSubmitLabel.value = null;
  loading.value = false;
};
</script>
