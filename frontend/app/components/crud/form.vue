<template>
  <UForm
    ref="form"
    :state="formData"
    :validate-on="['input', 'change']"
    :validate="validate"
    :schema="formSchema"
    :loading="loading"
    class="mx-auto"
    @submit="save()"
  >
    <div :class="`grid gap-4 ${gridCols}`">
      <template v-for="field in formFields" :key="field.key">
        <UFormField
          :name="field.key"
          :label="field.type !== 'checkbox' ? field.label : undefined"
          :required="field.required"
          :hint="field.hint"
        >
          <UInput
            v-if="field.type === 'text' || field.type === 'password'"
            v-model="formData[field.key] as string"
            class="w-full"
            :placeholder="field.placeholder"
            :icon="field.icon"
            :required="field.required"
            :type="field.type"
            :size="field.size || 'lg'"
            :disabled="field.disabled === true"
          />
          <UInputNumber
            v-if="field.type === 'number'"
            v-model="formData[field.key] as number"
            class="w-full"
            :placeholder="field.placeholder"
            :min="field.min"
            :max="field.max"
            :step="field.step"
            :required="field.required"
            :size="field.size || 'lg'"
            :disabled="field.disabled === true"
          />
          <UTextarea
            v-else-if="field.type === 'textarea'"
            v-model="formData[field.key] as any"
            class="w-full"
            :placeholder="field.placeholder"
            :required="field.required"
            :rows="5"
            :disabled="field.disabled === true"
          />
          <USelectMenu
            v-else-if="field.type === 'select' || field.type === 'multiselect'"
            v-model="formData[field.key] as any"
            class="w-full"
            :placeholder="field.placeholder"
            :items="field.options"
            value-key="value"
            label-key="label"
            :required="field.required"
            :multiple="field.type === 'multiselect'"
            :avatar="
              (Array.isArray(field.options)
                ? field.options.find(
                    (option: FilterOption) =>
                      option.value === formData[field.key],
                  )?.avatar
                : undefined) || field.avatar
            "
            :icon="
              (Array.isArray(field.options)
                ? field.options.find(
                    (option: FilterOption) =>
                      option.value === formData[field.key],
                  )?.icon
                : undefined) || field.icon
            "
            leading
            :disabled="field.disabled === true"
          >
            <template v-if="field.clearable" #trailing>
              <UIcon
                v-if="
                  formData[field.key] === null ||
                  formData[field.key] === undefined
                "
                class="group-data-[state=open]:rotate-180 transition-transform duration-200"
                name="i-lucide-chevron-down"
              />
              <UButton
                v-else
                icon="i-lucide-x"
                variant="ghost"
                color="neutral"
                size="sm"
                @click="formData[field.key] = null"
              />
            </template>
          </USelectMenu>
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
              :size="field.size || 'lg'"
              :disabled="field.disabled === true"
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
            :description="field.fileUploadDescription"
            :required="field.required"
            :file-icon="field.icon"
            color="neutral"
            :size="field.size || 'xl'"
            highlight
            :disabled="field.disabled === true"
          />
        </UFormField>
      </template>
    </div>
  </UForm>
</template>

<script setup lang="ts">
import type { FilterOption, CrudConfig } from "~/types/crud";

const props = withDefaults(
  defineProps<{
    api: typeof useApi;
    config: CrudConfig;
    entity?: Record<string, unknown>;
    gridCols?: string;
  }>(),
  {
    gridCols: "grid-cols-1",
  },
);
const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
  "validation-change": [isValid: boolean];
  "new-loading": [newLoading: boolean];
}>();

const utils = useUtils();
const loading = ref(false);
const form = ref();
const isFileUpload = ref(false);

const formFields = computed(() => {
  if (props.entity && props.config.editFormFields) {
    return props.config.editFormFields;
  } else if (!props.entity && props.config.createFormFields) {
    return props.config.createFormFields;
  } else {
    return props.config.formFields || [];
  }
});

const formSchema = computed(() => {
  if (props.entity && props.config.editFormSchema) {
    return props.config.editFormSchema;
  } else if (!props.entity && props.config.createFormSchema) {
    return props.config.createFormSchema;
  } else {
    return props.config.formSchema;
  }
});

const formData = ref<Record<string, unknown>>({});

watch(
  [formFields, () => props.entity],
  () => {
    formData.value = initFormData();
  },
  { immediate: true },
);

function initFormData() {
  const data: Record<string, unknown> = {};
  for (const field of formFields.value) {
    if (field.type === "tags") {
      data[field.key] =
        props.entity && Array.isArray(props.entity[field.key])
          ? [...props.entity[field.key]]
          : [];
    } else if (field.type === "file") {
      data[field.key] = null;
      isFileUpload.value = true;
    } else {
      if (props.entity) {
        data[field.key] = props.entity[field.key] ?? "";
      }
    }
  }
  return data;
}

function validate(data) {
  if (formSchema.value) {
    try {
      formSchema.value?.parse(data);
      emit("validation-change", true);
    } catch {
      emit("validation-change", false);
    }
  }
}

function body() {
  if (!isFileUpload.value) {
    const data = { ...formData.value, ...(props.config.defaultBody || {}) };
    for (const field of formFields.value) {
      if (field.type === "password" && typeof data[field.key] === "string") {
        if (field.key === "confirmpassword" || /^\*+$/.test(data[field.key])) {
          delete data[field.key];
        }
      }
    }
    return data;
  } else {
    const body = new FormData();
    for (const field of Object.keys(props.config.defaultBody || {})) {
      body.append(field, props.config.defaultBody[field]);
    }
    for (const field of formFields.value) {
      if (field.key === "confirmpassword") continue;
      if (field.key in formData.value) {
        if (
          field.type === "password" &&
          typeof formData.value[field.key] === "string"
        ) {
          if (/^\*+$/.test(formData.value[field.key])) {
            continue;
          }
        }
        body.append(field.key, formData.value[field.key]);
      }
    }
    return body;
  }
}

function save() {
  loading.value = true;
  const request = props.entity
    ? props.api.update(
        props.config.putEndpoint !== undefined
          ? props.config.putEndpoint
          : props.entity.id
            ? `${props.entity.id}/`
            : "",
        body(),
        {},
        utils.firstUpper(props.config.entityName),
      )
    : props.api.create(
        "",
        body(),
        {},
        utils.firstUpper(props.config.entityName),
      );
  request
    .then((response) => {
      emit("submit", response);
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
