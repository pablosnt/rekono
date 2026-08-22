<template>
  <UForm
    ref="form"
    :state="formData"
    :validate-on="['input', 'change']"
    :validate="validate"
    :schema="schema"
    :loading="loading"
    class="mx-auto"
    @submit="save()"
  >
    <UAlert
      color="info"
      variant="subtle"
      icon="i-lucide-info"
      description="When a new finding matching the alert's criteria is found, subscribers will receive a notification"
      class="mb-3"
    />
    <UFormField name="item" label="Entity" required>
      <USelectMenu
        v-model="formData['item'] as any"
        class="w-full"
        placeholder="Select entity to receive alerts about"
        :items="alertItems"
        value-key="item"
        label-key="item"
        required
        :icon="
          formData['item']
            ? alertItems.find((alert) => alert.item === formData['item'])?.icon
            : undefined
        "
        leading
        :disabled="entity !== undefined"
        size="lg"
      />
    </UFormField>
    <UFormField
      v-if="
        formData['item'] &&
        ![null, 'trending'].includes(
          alertItems.find((alert) => alert.item == formData['item'])?.field ||
            null,
        )
      "
      class="mt-3"
      name="value"
      label="Filter"
    >
      <UInput
        v-model="formData['value'] as string"
        class="w-full"
        :placeholder="`Filter by ${smartLowerCase((alertItems.find((alert) => alert.item == formData['item'])?.field || '').toUpperCase())}`"
        size="lg"
      />
    </UFormField>
    <UFormField name="item" class="mt-3">
      <UCheckbox
        v-if="!entity"
        v-model="formData['subscribe_all_members'] as boolean"
        label="Subscribe all members by default"
      />
    </UFormField>
  </UForm>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import { alertItems } from "~/constants";
import * as z from "zod";

const props = defineProps<{
  api: typeof useApi;
  config: CrudConfig;
  entity?: Record<string, unknown>;
}>();
const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
  "validation-change": [isValid: boolean];
  "new-loading": [newLoading: boolean];
  error: [error: object];
}>();

const route = useRoute();
const validation = useValidation();
const formData = ref<Record<string, unknown>>({
  project: parseInt(route.params.project_id),
  item: props.entity ? props.entity.item : undefined,
  value: props.entity ? props.entity.value : undefined,
  subscribe_all_members: !props.entity,
});
const schema = z.object({
  item: z.string(),
  value: validation.name("value", false, 100),
  subscribe_all_members: z.boolean().optional(),
});
const loading = ref(false);
const form = ref();

function validate(data) {
  if (schema) {
    try {
      schema.parse(data);
      emit("validation-change", true);
    } catch {
      emit("validation-change", false);
    }
  }
}

function save() {
  loading.value = true;
  emit("new-loading", true);
  const entityName = firstUpper(props.config.entityName);
  const request = props.entity
    ? props.api.update(
        props.entity.id ? `${props.entity.id}/` : "",
        formData.value,
        {},
        entityName,
      )
    : props.api.create("", formData.value, {}, entityName);
  request
    .then((response) => {
      emit("submit", response);
    })
    .catch((error) => {
      emit("error", error);
    })
    .finally(() => {
      loading.value = false;
      emit("new-loading", false);
    });
}

function submit() {
  form.value.submit();
}

defineExpose({ submit });
</script>
