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
    <UFormField
      v-if="!entity"
      name="target"
      label="Target"
      hint="Filter report's findings by target"
    >
      <USelectMenu
        v-model="formData.target"
        class="w-full"
        :icon="
          formData.target
            ? targetOptions.find((t) => t.value === formData.target)?.icon
            : 'i-lucide-locate-fixed'
        "
        placeholder="Select a target"
        :items="targetOptions"
        value-key="value"
        size="lg"
      >
        <template #trailing>
          <UIcon
            v-if="!formData.target"
            class="group-data-[state=open]:rotate-180 transition-transform duration-200"
            name="i-lucide-chevron-down"
          />
          <UButton
            v-else
            icon="i-lucide-x"
            variant="ghost"
            color="neutral"
            size="sm"
            aria-label="Clear target"
            @click="formData.target = undefined"
          />
        </template>
      </USelectMenu>
    </UFormField>
    <UFormField name="format" label="Format" required class="mt-3">
      <USelectMenu
        v-model="formData.format"
        class="w-full"
        :icon="
          formData.format
            ? reportFormats.find((f) => f.value === formData.format)?.icon
            : 'i-lucide-file-type'
        "
        placeholder="Select format"
        :items="reportFormats"
        value-key="value"
        label-key="label"
        size="lg"
        required
      />
    </UFormField>
    <UFormField name="only_true_positives" class="mt-3">
      <UCheckbox
        v-model="formData.only_true_positives"
        label="Only true positives"
      />
    </UFormField>
    <UFormField name="include_findings_from_user_input" class="mt-3">
      <UCheckbox
        v-model="formData.include_findings_from_user_input"
        label="Include findings derived from manual inputs like targets, ports, etc."
      />
    </UFormField>
    <UFormField
      v-if="formData.format !== 'pdf'"
      name="finding_types"
      label="Finding Types"
      class="mt-3"
    >
      <USelectMenu
        v-model="formData.finding_types"
        class="w-full"
        icon="i-lucide-layers"
        placeholder="Select finding types"
        :items="findingTypes"
        value-key="value"
        label-key="value"
        multiple
        size="lg"
      >
        <template #label>
          <div
            v-if="formData.finding_types?.length"
            class="flex gap-1 flex-wrap"
          >
            <UBadge
              v-for="type in formData.finding_types"
              :key="type"
              variant="subtle"
              size="sm"
            >
              <UIcon
                :name="findingTypes.find((f) => f.value === type)?.icon"
                class="w-3 h-3 mr-1"
              />
              {{ findingTypes.find((f) => f.value === type)?.label }}
            </UBadge>
          </div>
        </template>
      </USelectMenu>
    </UFormField>
  </UForm>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import * as z from "zod";
import { reportFormats, findingTypes } from "~/constants";

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

const options = useOptions();
const route = useRoute();
const toast = useToast();
const targetOptions = ref([]);
const formData = ref<Record<string, unknown>>({
  project: parseInt(route.params.project_id),
  target: props.entity ? props.entity.target : undefined,
  task: props.entity ? props.entity.task : undefined,
  format: "pdf",
  only_true_positives: false,
  include_findings_from_user_input: false,
  finding_types: findingTypes.map((t) => t.value),
});
const schema = z.object({
  target: z.number().optional(),
  task: z.number().optional(),
  format: z.string(),
  only_true_positives: z.boolean(),
  include_findings_from_user_input: z.boolean(),
  finding_types: z.array(z.string()).optional(),
});
const loading = ref(false);
const form = ref();

onMounted(() => {
  options.targets(targetOptions, { project: route.params.project_id });
  validate(formData.value);
});

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
  props.api
    .create(
      "",
      formData.value,
      {},
      firstUpper(props.config.entityName),
      [400, 401, 403, 429, 500],
    )
    .then((response) => {
      emit("submit", response);
    })
    .catch((error) => {
      if (error.statusCode === 404) {
        toast.add({
          title: "No Findings",
          description: "No findings matching the report criteria",
          color: "warning",
        });
      }
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
