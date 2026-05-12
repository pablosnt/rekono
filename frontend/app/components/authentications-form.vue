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
    <div class="grid gap-4">
      <UFormField label="Authentication Type" name="type" :required="true">
        <USelectMenu
          v-model="formData.type"
          :items="authenticationTypes"
          class="w-full"
          size="lg"
          required
          leading
        >
          <template #trailing>
            <UIcon
              v-if="formData.type === null || formData.type === undefined"
              class="group-data-[state=open]:rotate-180 transition-transform duration-200"
              name="i-lucide-chevron-down"
            />
            <UButton
              v-else
              icon="i-lucide-x"
              variant="ghost"
              color="neutral"
              size="sm"
              aria-label="Remove authentication"
              @click="formData.type = 'None'"
            />
          </template>
        </USelectMenu>
      </UFormField>
      <UFormField v-if="formData.type !== 'None'" :label="labels.name" required>
        <UInput
          v-model="formData.name"
          :placeholder="labels.name"
          class="w-full"
          size="lg"
        />
      </UFormField>
      <UFormField
        v-if="formData.type !== 'None'"
        :label="labels.secret"
        required
      >
        <UInput
          v-model="formData.secret"
          type="password"
          :placeholder="labels.secret"
          class="w-full"
          size="lg"
        />
      </UFormField>
    </div>
  </UForm>
</template>

<script setup lang="ts">
import * as z from "zod";
import type { CrudConfig } from "~/types/crud";
import type { TargetPort } from "~/types/models";
import { authenticationTypes } from "~/constants";

const props = defineProps<{ entity: TargetPort; config: CrudConfig }>();
const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
  "validation-change": [isValid: boolean];
  "new-loading": [newLoading: boolean];
  error: [error: object];
}>();

const validation = useValidation();
const form = ref();
const formData = ref({
  target_port: props.entity.id,
  type: "None",
  name: undefined,
  secret: undefined,
});
emit("validation-change", true);
const formSchema = z.object({
  type: z.enum(authenticationTypes),
  name: validation.name("name", formData.value.type !== "None", 100),
  secret: validation.secret("secret", formData.value.type !== "None", 500),
});
const loading = ref(false);
const labels = computed(() => {
  if (formData.value.type) {
    switch (formData.value.type) {
      case "Basic":
        return { name: "Username", secret: "Password" };
      case "Bearer":
      case "JWT":
      case "Digest":
      case "Token":
        return { name: "Token Name", secret: "Token" };
      case "Cookie":
        return { name: "Cookie Name", secret: "Cookie Value" };
      default:
        return { name: "Name", secret: "Secret" };
    }
  } else {
    return { name: "Name", secret: "Secret" };
  }
});

function validate(data) {
  if (formSchema) {
    try {
      formSchema.parse(data);
      emit("validation-change", true);
    } catch {
      emit("validation-change", false);
    }
  }
}

function save() {
  if (formData.value.type !== "None") {
    loading.value = true;
    emit("new-loading", true);
    useApi(props.config.endpoint)
      .create("", formData.value, {}, firstUpper(props.config.entityName))
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
  } else {
    emit("submit", { type: "None" });
  }
}

function submit() {
  form.value.submit();
}

defineExpose({ submit });
</script>
