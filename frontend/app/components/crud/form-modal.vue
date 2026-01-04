<template>
  <UModal
    :open="open"
    :title="modalTitle"
    :fullscreen="config.formFullscreen ? true : false"
    :ui="{
      content: config.formFullscreen ? '' : 'sm:max-w-3xl sm:max-h-xl',
      footer: 'justify-end',
    }"
    @update:open="(value: boolean) => $emit('open', value)"
  >
    <template #body>
      <component
        :is="formComponent"
        ref="form"
        :api="api"
        :config="config"
        :entity="item"
        @submit="handleSubmit"
        @new-title="(newTitle: string) => (modalTitle = newTitle)"
        @new-submit-label="
          (newSubmitLabel: string) => (submitButton = newSubmitLabel)
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
      <UButton color="primary" :label="submitButton" @click="form?.submit()" />
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
const modalTitle = ref(
  props.title ||
    (props.item
      ? `Edit ${props.config.entityName}`
      : `New ${props.config.entityName}`),
);
const submitButton = ref(props.submitLabel || (props.item ? "Save" : "Create"));

const handleSubmit = () => {
  emit("submit");
  emit("open", false);
};
</script>
