<!-- TODO: Define Steps form that must be shown in the edit modal and in a specific modal when one row is clicked -->
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
                  $emit('new-submit-label', 'Continue');
                  $emit('new-title', data.name);
                }
              "
            />
          </template>
          <template v-else>
            <div class="text-center py-8">
              <UIcon
                name="i-lucide-construction"
                class="text-4xl text-gray-400 mb-4"
              />
              <h3 class="text-lg font-medium text-gray-600 dark:text-gray-400">
                Steps Configuration
              </h3>
              <p class="text-gray-500 dark:text-gray-500 mt-2">
                This step will be implemented to configure process steps.
              </p>
            </div>
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
    emit("submit");
  }
}

defineExpose({ submit });
</script>
