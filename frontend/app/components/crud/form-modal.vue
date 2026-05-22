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
    <template #header="{ close }">
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-2">
          <UAvatar v-if="modalAvatar" v-bind="modalAvatar" />
          <UIcon
            v-else-if="modalIcon"
            :name="modalIcon"
            :class="config.modalIconClass || 'text-xl text-primary'"
          />
          <h2 class="text-gray-900 dark:text-white font-bold text-lg">
            {{ modalTitle }}
          </h2>
        </div>
        <div class="flex items-center gap-2">
          <slot name="before-close" :loading="loading" />
          <UButton
            icon="i-lucide-x"
            variant="ghost"
            color="neutral"
            aria-label="Close"
            @click="close"
          />
        </div>
      </div>
    </template>
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
        @new-loading="(newLoading: boolean) => (loading = newLoading)"
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
  api: typeof useApi;
  title?: string;
  submitLabel?: string;
  ui?: Record<string, unknown>;
}>();

const emit = defineEmits<{
  open: [open: boolean];
  submit: [data: Record<string, unknown>];
}>();

const form = ref();
const formComponent = computed(
  () =>
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
const modalAvatar = computed(() => {
  return props.config.modalAvatar && props.item
    ? props.config.modalAvatar(props.item) || undefined
    : undefined;
});
const modalIcon = computed(() => {
  return props.config.modalIcon
    ? typeof props.config.modalIcon === "string"
      ? props.config.modalIcon
      : props.item
        ? props.config.modalIcon(props.item)
        : undefined
    : undefined;
});
const updatedSubmitLabel = ref();
const submitButton = computed(
  () =>
    updatedSubmitLabel.value ||
    props.submitLabel ||
    (props.item ? "Save" : "Create"),
);
const formValid = ref(!!props.item);
const loading = ref(false);

const handleSubmit = (data: Record<string, unknown>) => {
  if (props.config.onCreation) {
    props.config.onCreation(data);
  }
  emit("submit", data);
  emit("open", false);
  updatedTitle.value = null;
  updatedSubmitLabel.value = null;
  loading.value = false;
};
</script>
