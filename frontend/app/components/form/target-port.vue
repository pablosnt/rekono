<template>
  <UStepper
    v-model="stepper"
    :items="[
      { title: 'Target Port', icon: 'i-lucide-ethernet-port' },
      { title: 'Authentication', icon: 'i-lucide-key' },
    ]"
    disabled
  >
    <template #content="{ item }">
      <UContainer>
        <template v-if="item.title === 'Target Port'">
          <CrudForm
            ref="targetPortForm"
            :api="api"
            :config="config"
            @submit="
              (data) => {
                targetPort = data;
                stepper = 1;
                $emit('new-submit-label', 'Save');
                $emit('new-loading', false);
              }
            "
            @validation-change="
              (isValid) => $emit('validation-change', isValid)
            "
          />
        </template>
        <template v-else>
          <FormAuthentication
            ref="authenticationForm"
            :entity="targetPort"
            :config="{
              endpoint: '/api/authentications/',
              entityName: 'Authentication',
            }"
            @new-loading="(newLoading) => $emit('new-loading', newLoading)"
            @validation-change="
              (isValid) => $emit('validation-change', isValid)
            "
            @submit="$emit('submit', $event)"
          />
        </template>
      </UContainer>
    </template>
  </UStepper>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";

defineProps<{
  api: typeof useApi;
  config: CrudConfig;
  entity?: Record<string, unknown>;
}>();
defineEmits<{
  submit: [data: Record<string, unknown>];
  "new-submit-label": [newSubmitLabel: string];
  "new-loading": [newLoading: boolean];
  "validation-change": [isValid: boolean];
}>();

const stepper = ref(0);
const targetPortForm = ref();
const authenticationForm = ref();
const targetPort = ref();

function submit() {
  if (stepper.value === 0) {
    targetPortForm.value.submit();
  } else {
    authenticationForm.value.submit();
  }
}

defineExpose({ submit });
</script>
