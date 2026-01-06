<template>
  <div>
    <UStepper
      v-model="stepper"
      :items="[
        {
          title: 'Process',
          description: 'Define process details',
          icon: 'i-lucide-workflow',
        },
        {
          title: 'Steps',
          description: 'Configure process steps',
          icon: 'i-lucide-play-circle',
        },
      ]"
      :disabled="!process"
    >
      <template #content="{ item }">
        <UContainer>
          <template v-if="item.title === 'Process'">
            <CrudForm
              ref="processFormRef"
              :api="api"
              :config="config"
              :entity="process || entity"
              @submit="
                (data) => {
                  process = data;
                  stepper = 1;
                  $emit('new-submit-label', 'Save');
                  $emit('new-title', data.name);
                }
              "
            />
          </template>
          <template v-else>
            <ProcessStepsForm :process="process" />
          </template>
        </UContainer>
      </template>
    </UStepper>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";

const props = defineProps<{
  api: object;
  config: CrudConfig;
  entity?: Record<string, unknown>;
}>();

const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
  "new-title": [newTitle: string];
  "new-submit-label": [newSubmitLabel: string];
}>();

const processFormRef = ref();
const stepper = ref(0);
const process = ref(props.entity || null);

function submit() {
  if (stepper.value === 0) {
    processFormRef.value.submit();
  } else {
    emit("submit", process.value);
  }
}

defineExpose({ submit });
</script>
