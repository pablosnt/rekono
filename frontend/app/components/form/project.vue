<template>
  <div>
    <UStepper
      v-model="stepper"
      :items="[
        {
          title: 'Project',
          description: 'Define project details',
          icon: 'i-lucide-folder',
        },
        {
          title: 'Targets',
          description: 'Add targets to the project',
          icon: 'i-lucide-locate-fixed',
        },
      ]"
      :disabled="!project"
    >
      <template #content="{ item }">
        <UContainer>
          <template v-if="item.title === 'Project'">
            <CrudForm
              ref="projectFormRef"
              :api="api"
              :config="config"
              :entity="project"
              @submit="
                (data) => {
                  project = data;
                  stepper = 1;
                  $emit('new-title', data.name);
                  $emit('new-loading', false);
                }
              "
              @validation-change="
                (isValid) => $emit('validation-change', isValid)
              "
            />
          </template>
          <template v-else>
            <FormTarget
              ref="targetFormRef"
              :api="targetApi"
              :entity="project"
              @submit="(data) => $emit('submit', data)"
            />
          </template>
        </UContainer>
      </template>
    </UStepper>
  </div>
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
  "new-title": [newTitle: string];
  "new-submit-label": [newSubmitLabel: string];
  "new-loading": [newLoading: boolean];
  "validation-change": [isValid: boolean];
}>();

const targetApi = useApi("/api/targets/");
const projectFormRef = ref();
const targetFormRef = ref();
const stepper = ref(0);
const project = ref(null);

async function submit() {
  if (stepper.value === 0) {
    projectFormRef.value.submit();
  } else {
    targetFormRef.value.submit();
  }
}

defineExpose({ submit });
</script>
