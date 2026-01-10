<template>
  <UStepper v-model="stepper" :items="stepperItems">
    <template #content="{ item }">
      <UForm class="space-y-4 mx-auto mt-3">
        <template v-if="item.title === 'Target'">
          <UFormField
            v-if="!entity.project && !entity.target"
            required
            label="Project"
          >
            <USelectMenu
              :model-value="project"
              class="w-full"
              icon="i-lucide-folder"
              placeholder="Select a project"
              :items="projectOptions"
              value-key="id"
              label-key="name"
              description-key="none"
              size="xl"
              required
              leading
              @update:model-value="
                (value) => {
                  project = value;
                  onProject();
                }
              "
            >
              <template #trailing>
                <UIcon
                  v-if="project === null || project === undefined"
                  class="group-data-[state=open]:rotate-180 transition-transform duration-200"
                  name="i-lucide-chevron-down"
                />
                <UButton
                  v-else
                  icon="i-lucide-x"
                  variant="ghost"
                  color="neutral"
                  size="sm"
                  @click="project = null"
                />
              </template>
            </USelectMenu>
          </UFormField>
          <UFormField v-if="!entity.target" required label="Target">
            <USelectMenu
              :model-value="target"
              class="w-full"
              icon="i-lucide-locate-fixed"
              placeholder="Select a target"
              :items="targetOptions"
              value-key="id"
              label-key="target"
              size="xl"
              required
              :disabled="!project"
              leading
              @update:model-value="
                (value) => {
                  target = value;
                  onTarget();
                }
              "
            >
              <template #trailing>
                <UIcon
                  v-if="target === null || target === undefined"
                  class="group-data-[state=open]:rotate-180 transition-transform duration-200"
                  name="i-lucide-chevron-down"
                />
                <UButton
                  v-else
                  icon="i-lucide-x"
                  variant="ghost"
                  color="neutral"
                  size="sm"
                  @click="target = null"
                />
              </template>
            </USelectMenu>
          </UFormField>
          <UFormField v-if="!entity.targetPort" label="Target Port">
            <!-- TODO: Customize target port icon based on the port number as we did on the old frontend -->
            <USelectMenu
              :model-value="targetPort"
              class="w-full"
              icon="i-lucide-network"
              placeholder="Select a target port"
              :items="
                targetPortOptions.map((port) => ({
                  id: port.id,
                  label: port.path
                    ? `${port.port} - ${port.path}`
                    : port.port.toString(),
                }))
              "
              value-key="id"
              label-key="label"
              size="xl"
              :disabled="!target"
              leading
              @update:model-value="(value) => (targetPort = value)"
            >
              <template #trailing>
                <UIcon
                  v-if="targetPort === null || targetPort === undefined"
                  class="group-data-[state=open]:rotate-180 transition-transform duration-200"
                  name="i-lucide-chevron-down"
                />
                <UButton
                  v-else
                  icon="i-lucide-x"
                  variant="ghost"
                  color="neutral"
                  size="sm"
                  @click="targetPort = null"
                />
              </template>
            </USelectMenu>
          </UFormField>
        </template>
        <template v-if="item.title === 'Tooling'"></template>
        <template v-if="item.title === 'Intensity'">
          <UFormField required>
            <USlider
              class="mt-8 mb-2"
              :model-value="intensity"
              :min="1"
              :max="5"
              :default-value="3"
              :tooltip="{
                text: utils.intensityOptions[intensity - 1].label,
                open: true,
                content: {
                  side: 'top',
                  sideOffset: 8,
                  collisionPadding: 8,
                },
              }"
              :color="utils.intensityOptions[intensity - 1]?.color"
              @update:model-value="(value) => (intensity = value)"
            />
          </UFormField>
        </template>
        <template v-if="item.title === 'Wordlists'"></template>
        <template v-if="item.title === 'Technologies'"></template>
        <template v-if="item.title === 'Vulnerabilities'"></template>
        <template v-if="item.title === 'Schedule'"></template>
        <template v-if="item.title === 'Monitor'"></template>
      </UForm>
    </template>
  </UStepper>
</template>

<script setup lang="ts">
import type { FormError } from "@nuxt/ui";
import type { CrudConfig } from "~/types/crud";

const props = defineProps<{
  api: object;
  config?: CrudConfig;
  entity?: Record<string, unknown>;
}>();
const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
  "validation-change": [isValid: boolean];
}>();
emit("validation-change", false);

const genericApi = useApi("/api/");
const utils = useUtils();
const stepperItems = computed(() => {
  const items = [];
  if (!props.entity.targetPort) {
    items.push({
      title: "Target",
      icon: "i-lucide-locate-fixed",
    });
  }
  if (!props.entity.configuration && !props.entity.process) {
    items.push({
      title: "Tooling",
      description: "Choose tool or process",
      icon: "i-lucide-terminal",
    });
  }
  items.push({
    title: "Intensity",
    icon: "i-lucide-zap",
  });
  if (wordlistOptions.value.length > 0) {
    items.push({
      title: "Wordlists",
      description: "Customize wordlists",
      icon: "i-lucide-list",
    });
  }
  if (inputTechnologyOptions.value.length > 0) {
    items.push({
      title: "Technologies",
      description: "Provide technologies to scan",
      icon: "i-lucide-cpu",
    });
  }
  if (inputVulnerabilityOptions.value.length > 0) {
    items.push({
      title: "Vulnerabilities",
      description: "Provide vulnerabilities to scan",
      icon: "i-lucide-shield-alert",
    });
  }
  items.push(
    {
      title: "Schedule",
      //   description: "Set execution time",
      icon: "i-lucide-calendar",
    },
    {
      title: "Monitor",
      description: "Scan periodically",
      icon: "i-lucide-repeat",
    },
  );
  return items;
});
const stepper = ref(0);
const loading = ref(false);

const project = ref(props.entity.project);
const projectOptions = ref([]);
const target = ref(props.entity.target);
const targetOptions = ref([]);
const targetPort = ref(props.entity.targetPort);
const targetPortOptions = ref([]);
const process = ref(props.entity.process);
const processOptions = ref([]);
const tool = ref(props.entity.tool);
const toolOptions = ref([]);
const configuration = ref(props.entity.configuration);
const configurationOptions = ref([]);
const intensity = ref(3);
const wordlists = ref([]);
const wordlistOptions = ref([]);
const wordlistType = ref();
const requiredWordlist = ref(false);
const inputTechnologies = ref([]);
const inputTechnologyOptions = ref([]);
const requiredInputTechnology = ref(false);
const inputVulnerabilities = ref([]);
const inputVulnerabilityOptions = ref([]);
const requiredInputVulnerability = ref(false);
const scheduledAt = ref();
const repeatIn = ref();
const repeatTimeUnit = ref("Days");

function loadProjects() {
  genericApi.list("projects/", {}, true).then((response) => {
    projectOptions.value = response.items;
  });
}

function onProject() {
  target.value = null;
  targetPort.value = null;
  if (project.value) {
    genericApi
      .list("targets/", { project: project.value }, true)
      .then((response) => {
        targetOptions.value = response.items;
      });
  }
}

function onTarget() {
  targetPort.value = null;
  if (target.value) {
    genericApi
      .list("target-ports/", { target: target.value }, true)
      .then((response) => {
        targetPortOptions.value = response.items;
      });
  } else {
    targetPortOptions.value = [];
  }
}

function loadTooling() {
  genericApi.list("tools/", {}, true).then((response) => {
    toolOptions.value = response.items;
  });
  genericApi.list("processes/", {}, true).then((response) => {
    processOptions.value = response.items;
  });
}

function onTool() {
  if (tool.value) {
    process.value = null;
    configuration.value = null;
    genericApi
      .list("configurations/", { tool: tool.value }, true)
      .then((response) => {
        configurationOptions.value = response.items;
      });
  }
}

function onConfiguration() {
  if (configuration.value) {
    genericApi
      .get(`configurations/${configuration.value}/`)
      .then((response) => {
        if (response.wordlists.supported) {
          if (wordlistOptions.value.length === 0) {
            loadWordlists();
          }
          requiredWordlist.value = response.wordlists.required;
        }
        if (response.input_technologies.supported) {
          if (inputTechnologyOptions.value.length === 0) {
            genericApi
              .list("input-technologies/", {}, true)
              .then((response) => {
                inputTechnologyOptions.value = response.items;
              });
          }
          requiredInputTechnology.value = response.input_technologies.required;
        }
        if (response.input_vulnerabilities.supported) {
          if (inputVulnerabilityOptions.value.length === 0) {
            genericApi
              .list("input-vulnerabilities/", {}, true)
              .then((response) => {
                inputVulnerabilityOptions.value = response.items;
              });
          }
          requiredInputVulnerability.value =
            response.input_vulnerabilities.required;
        }
      });
  }
}

function onProcess() {
  if (process.value) {
    tool.value = null;
    configuration.value = null;
    genericApi.get(`processes/${process.value}/`).then((response) => {
      if (response.wordlists.supported) {
        if (wordlistOptions.value.length == 0) {
          loadWordlists();
        }
        requiredWordlist.value = response.wordlists.required;
      }
    });
  }
}

function loadWordlists() {
  genericApi
    .list("wordlists/", wordlistType.value ? { type: wordlistType } : {}, true)
    .then((response) => {
      wordlistOptions.value = response.items;
    });
}

function validate(data: Record<string, unknown>): FormError[] {
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
        target_port: targetPort.value,
        process_id: process.value,
        configuration_id: configuration.value,
        intensity: utils.intensityOptions[intensity.value - 1]?.label,
        scheduled_at: scheduledAt.value, // TODO: Review format
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

onMounted(() => {
  if (!project.value && !target.value) {
    loadProjects();
  } else if (target.value) {
    onTarget();
  } else if (project.value) {
    onProject();
  }
  if (!tool.value && !configuration.value && !process.value) {
    loadTooling();
  } else if (configuration.value) {
    onConfiguration();
  } else if (tool.value) {
    onTool();
  } else if (process.value) {
    onProcess();
  }
});

defineExpose({ submit });
</script>
