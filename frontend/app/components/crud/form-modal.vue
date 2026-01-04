<template>
  <UModal
    :open="open"
    :title="
      title || (item ? `Edit ${config.entityName}` : `New ${config.entityName}`)
    "
    :fullscreen="config.formFullscreen ? true : false"
    :ui="{
      content: config.formFullscreen ? '' : 'sm:max-w-3xl sm:max-h-xl',
      footer: 'justify-end',
    }"
    @update:open="(value: boolean) => $emit('open', value)"
  >
    <template #body>
      <!-- TODO: Customize the formComponent based o creation/edition -->
      <component
        :is="formComponent"
        ref="form"
        :api="api"
        :config="config"
        :entity="item"
        @submit="handleSubmit"
        @new-entity="(newEntity: object) => $emit('new-entity', newEntity)"
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
        @click="form?.submit()"
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
}>();

const emit = defineEmits<{
  open: [open: boolean];
  submit: [];
  "new-entity": [newEntity: object];
}>();

const form = ref();
const formComponent = ref(
  props.config.formComponent || resolveComponent("CrudForm"),
);

const handleSubmit = () => {
  emit("submit");
  emit("open", false);
};
</script>
