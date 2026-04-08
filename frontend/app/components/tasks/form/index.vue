<template>
  <UStepper
    ref="stepper"
    v-model="stepperStep"
    :items="stepperItems"
    :linear="false"
  >
    <template #content="{ item }">
      <UForm
        :validate-on="['input', 'change']"
        :validate="validate"
        :loading="loading"
      >
        <TasksFormTarget
          v-show="item.title === 'Target'"
          :api="genericApi"
          :default-project="entity.project"
          :default-target="entity.target"
          @update-project="
            (newProject: number | undefined) => (project = newProject)
          "
          @update-target="
            (newTarget: number | undefined) => (target = newTarget)
          "
          @update-target-port="
            (newTargetPort: number | undefined) => (targetPort = newTargetPort)
          "
          @update-target-port-options="
            (hasOptions: boolean) => (hasTargetPortOptions = hasOptions)
          "
        />
        <TasksFormScanner
          v-show="item.title === 'Scanner'"
          :api="genericApi"
          :default-tool="entity.tool"
          :default-configuration="entity.configuration"
          :default-process="entity.process"
          @update-tool="(newTool) => (tool = newTool)"
          @update-configuration="
            (newConfiguration) => (configuration = newConfiguration)
          "
          @update-process="(newProcess) => (process = newProcess)"
          @update-wordlist="
            (supported, required) => {
              supportedWordlist = supported;
              requiredWordlist = required;
              if (!supported) {
                wordlists = [];
              }
            }
          "
          @update-input-technology="
            (required) => {
              requiredInputTechnology = required;
              if (!required) {
                inputTechnologies = [];
              }
            }
          "
          @update-input-vulnerability="
            (required) => {
              requiredInputVulnerability = required;
              if (!required) {
                inputVulnerabilities = [];
              }
            }
          "
          @update-intensity="
            (newMinIntensity, newMaxIntensity) => {
              minIntensity = newMinIntensity;
              maxIntensity = newMaxIntensity;
              if (minIntensity === maxIntensity) {
                intensity = minIntensity;
              }
            }
          "
        />
        <TasksFormIntensity
          v-show="item.title === 'Intensity'"
          :is-process-selected="process !== null && process !== undefined"
          :min-intensity="minIntensity"
          :max-intensity="maxIntensity"
          @update-intensity="(newIntensity) => (intensity = newIntensity)"
        />
        <TasksFormWordlists
          v-show="item.title === 'Wordlists'"
          :api="genericApi"
          :supported-wordlist="supportedWordlist"
          :required-wordlist="requiredWordlist"
          @update-wordlists="(newWordlists) => (wordlists = newWordlists)"
        />
        <TasksFormTechnologies
          v-show="item.title === 'Technologies'"
          :api="genericApi"
          :required="requiredInputTechnology"
          @update-technologies="
            (newTechnologies) => (inputTechnologies = newTechnologies)
          "
        />
        <TasksFormVulnerabilities
          v-show="item.title === 'Vulnerabilities'"
          :api="genericApi"
          :required="requiredInputVulnerability"
          @update-vulnerabilities="
            (newVulnerabilities) => (inputVulnerabilities = newVulnerabilities)
          "
        />
        <TasksFormSchedule
          v-show="item.title === 'Schedule'"
          @update-scheduled-at="
            (newScheduledAt) => (scheduledAt = newScheduledAt)
          "
          @update-repeat-in="(newRepeatIn) => (repeatIn = newRepeatIn)"
          @update-repeat-time-unit="
            (newRepeatTimeUnit) => (repeatTimeUnit = newRepeatTimeUnit)
          "
        />
      </UForm>
      <div class="flex gap-2 justify-between mt-4">
        <UButton
          color="neutral"
          leading-icon="i-lucide-chevron-left"
          :disabled="!stepper?.hasPrev"
          @click="stepper?.prev()"
        />
        <UButton
          color="neutral"
          trailing-icon="i-lucide-chevron-right"
          :disabled="!stepper?.hasNext"
          @click="stepper?.next()"
        />
      </div>
    </template>
  </UStepper>
</template>

<script setup lang="ts">
import type { FormError } from "@nuxt/ui";
import type { CrudConfig } from "~/types/crud";

const props = defineProps<{
  api: typeof useApi;
  config?: CrudConfig;
  entity?: Record<string, unknown>;
}>();
const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
  "validation-change": [isValid: boolean];
}>();
emit("validation-change", false);

const genericApi = useApi("/api/");
const stepperItems = computed(() => {
  const items = [];
  if (
    (!props.entity.targetPort && hasTargetPortOptions.value) ||
    !props.entity.project ||
    !props.entity.target
  ) {
    items.push({
      title: "Target",
      icon: "i-lucide-locate-fixed",
    });
  }
  if (!props.entity.configuration && !props.entity.process) {
    items.push({
      title: "Scanner",
      description: "Tool or process to run",
      icon: "i-lucide-terminal",
    });
  }
  if (minIntensity.value < maxIntensity.value) {
    items.push({
      title: "Intensity",
      icon: "i-lucide-gauge",
    });
  }
  if (supportedWordlist.value) {
    items.push({
      title: "Wordlists",
      icon: "i-mdi-file-word",
    });
  }
  if (requiredInputTechnology.value) {
    items.push({
      title: "Technologies",
      description: "Provide input parameters",
      icon: "i-lucide-code",
    });
  }
  if (requiredInputVulnerability.value) {
    items.push({
      title: "Vulnerabilities",
      description: "Provide input parameters",
      icon: "i-lucide-bug",
    });
  }
  items.push({
    title: "Schedule",
    icon: "i-lucide-calendar-days",
  });
  return items;
});
const stepperStep = ref(0);
const stepper = useTemplateRef("stepper");
const loading = ref(false);

const project = ref(props.entity.project);
const target = ref(props.entity.target);
const targetPort = ref(props.entity.targetPort);
const hasTargetPortOptions = ref(true);
const process = ref(props.entity.process);
const tool = ref(props.entity.tool);
const configuration = ref(props.entity.configuration);
const intensity = ref(3);
const minIntensity = ref(1);
const maxIntensity = ref(5);
const wordlists = ref([]);
const supportedWordlist = ref(false);
const requiredWordlist = ref(false);
const inputTechnologies = ref([]);
const requiredInputTechnology = ref(false);
const inputVulnerabilities = ref([]);
const requiredInputVulnerability = ref(false);
const scheduledAt = ref(null);
const repeatIn = ref(null);
const repeatTimeUnit = ref("Days");

function validate(): FormError[] {
  if (
    project.value &&
    target.value &&
    (process.value || (tool.value && configuration.value)) &&
    intensity.value &&
    (wordlists.value.length > 0 || !requiredWordlist.value) &&
    (inputTechnologies.value.length > 0 || !requiredInputTechnology.value) &&
    (inputVulnerabilities.value.length > 0 || !requiredInputVulnerability.value)
  ) {
    emit("validation-change", true);
  } else {
    emit("validation-change", false);
  }
}

function submit() {
  loading.value = true;
  props.api
    .create(
      "",
      {
        target_id: target.value,
        target_port_id: targetPort.value,
        process_id: process.value,
        configuration_id: configuration.value,
        intensity: intensities[intensity.value - 1]?.label,
        scheduled_at: scheduledAt.value ? scheduledAt.value.toString() : null,
        repeat_in: repeatIn.value,
        repeat_time_unit: repeatTimeUnit.value,
        wordlists: wordlists.value,
        input_technologies: inputTechnologies.value,
        input_vulnerabilities: inputVulnerabilities.value,
      },
      {},
      "Scan",
    )
    .then((response) => {
      emit("submit", response);
    })
    .finally(() => {
      loading.value = false;
    });
}

defineExpose({ submit });
</script>
