<template>
  <UForm
    ref="form"
    :state="formData"
    :validate-on="['input', 'change']"
    :schema="config.formSchema"
    :loading="loading"
    class="space-y-4 mx-auto"
    @submit="save()"
  >
    <template v-for="field in config.formFields" :key="field.key">
      <UFormField
        :name="field.key"
        :label="field.label"
        :required="field.required"
        :hint="field.hint"
      >
        <UInput
          v-if="field.type === 'text' || field.type === 'number'"
          v-model="formData[field.key] as any"
          class="w-full"
          :placeholder="field.placeholder"
          :icon="field.icon"
          :required="field.required"
          :type="field.type"
          size="lg"
        />
        <UTextarea
          v-else-if="field.type === 'textarea'"
          v-model="formData[field.key] as any"
          class="w-full"
          :placeholder="field.placeholder"
          :required="field.required"
          :rows="5"
        />
        <USelect
          v-else-if="field.type === 'select' || field.type === 'multiselect'"
          v-model="formData[field.key] as any"
          class="w-full"
          :placeholder="field.placeholder"
          :options="getOptions(field)"
          value-key="value"
          option-key="label"
          :required="field.required"
          :multiple="field.type === 'multiselect'"
        />
        <UCheckbox
          v-else-if="field.type === 'checkbox'"
          v-model="formData[field.key] as any"
          :label="field.label"
        />
        <template v-else-if="field.type === 'tags'">
          <UInput
            class="w-full"
            :placeholder="
              field.placeholder || 'Type and press Enter to add tag'
            "
            :icon="field.icon"
            size="lg"
            @keydown.enter.prevent="
              (e: Event) => {
                const target = e.target as HTMLInputElement;
                const val = target.value.trim();
                if (val) {
                  if (!formData[field.key]) formData[field.key] = [];
                  if (!(formData[field.key] as string[]).includes(val)) {
                    (formData[field.key] as string[]).push(val);
                  }
                  target.value = '';
                }
              }
            "
          />
          <div
            v-if="
              Array.isArray(formData[field.key]) &&
              (formData[field.key] as string[]).length
            "
            class="flex flex-wrap gap-2 mt-2"
          >
            <UBadge
              v-for="(tag, index) in formData[field.key] as string[]"
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
                @click="(formData[field.key] as string[]).splice(index, 1)"
              />
            </UBadge>
          </div>
        </template>
        <UFileUpload
          v-else-if="field.type === 'file'"
          v-model="formData[field.key]"
          :accept="field.accept"
          :label="field.fileUploadLabel"
          variant="area"
          size="xl"
        />
      </UFormField>
    </template>
  </UForm>
</template>

<script setup lang="ts">
import type { FilterOption, CrudConfig, FormField } from "~/types/crud";

const props = defineProps<{
  api: typeof useApi;
  config: CrudConfig;
  entity?: Record<string, unknown>;
}>();
const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
}>();

const utils = useUtils();
const formData = ref<Record<string, unknown>>(initFormData());
const loading = ref(false);
const form = ref();

function getOptions(field: FormField): FilterOption[] {
  return Array.isArray(field.options) ? (field.options as FilterOption[]) : [];
}

function initFormData() {
  const data: Record<string, unknown> = {};
  for (const field of props.config.formFields || []) {
    if (field.type === "tags") {
      data[field.key] =
        props.entity && Array.isArray(props.entity[field.key])
          ? [...props.entity[field.key]]
          : [];
    } else if (field.type === "file") {
      data[field.key] = null;
    } else {
      if (props.entity) {
        data[field.key] = props.entity[field.key] ?? "";
      }
    }
  }
  return data;
}

function save() {
  loading.value = true;
  const request = props.entity
    ? props.api.update(
        `${props.entity.id}/`,
        formData.value,
        {},
        utils.firstUpper(props.config.entityName),
      )
    : props.api.create(
        "",
        formData.value,
        {},
        utils.firstUpper(props.config.entityName),
      );
  request
    .then((response) => {
      emit("submit", response);
    })
    .finally(() => {
      loading.value = false;
    });
}

function submit() {
  form.value.submit();
}

defineExpose({ submit });
</script>
