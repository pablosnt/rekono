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
        class="space-y-4 mx-auto mt-3"
      >
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
              :disabled="!project"
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
        <template v-if="item.title === 'Tooling'">
          <!-- TODO -->
        </template>
        <template v-if="item.title === 'Intensity'">
          <UFormField required>
            <USlider
              class="mt-8 mb-2"
              :model-value="intensity"
              :min="minIntensity"
              :max="maxIntensity"
              :default-value="3 < maxIntensity ? 3 : maxIntensity"
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
        <template v-if="item.title === 'Wordlists'">
          <UFormField
            v-if="wordlistOptions.length > 0"
            :required="requiredWordlist"
            label="Wordlists"
          >
            <USelectMenu
              :model-value="wordlists"
              multiple
              class="w-full"
              icon="i-lucide-file-text"
              placeholder="Select the wordlists to use"
              :items="wordlistOptions"
              value-key="id"
              label-key="name"
              description-key="type"
              :filter-fields="['name', 'type']"
              size="xl"
              @update:model-value="(value) => (wordlists = value)"
            >
              <template #trailing>
                <UIcon
                  v-if="wordlists.length === 0"
                  class="group-data-[state=open]:rotate-180 transition-transform duration-200"
                  name="i-lucide-chevron-down"
                />
                <UButton
                  v-else
                  icon="i-lucide-x"
                  variant="ghost"
                  color="neutral"
                  size="sm"
                  @click="wordlists = []"
                />
              </template>
            </USelectMenu>
          </UFormField>
        </template>
        <template v-if="item.title === 'Technologies'">
          <!-- TODO -->
        </template>
        <template v-if="item.title === 'Vulnerabilities'">
          <!-- TODO -->
        </template>
        <template v-if="item.title === 'Schedule'">
          <UFormField
            label="Datetime"
            hint="Schedule the execution start"
            class="text-center"
          >
            <UInputDate
              ref="inputScheduleDate"
              v-model="scheduledAt"
              class="w-100"
              :min-value="now(getLocalTimeZone())"
              size="xl"
              variant="outline"
              :hour-cycle="24"
              granularity="minute"
              @update:model-value="
                (datetime) => {
                  if (scheduledDate === null) {
                    scheduledDate = today(getLocalTimeZone());
                  }
                  if (datetime.year) {
                    scheduledDate.year = datetime.year;
                  }
                  if (datetime.month) {
                    scheduledDate.month = datetime.month;
                  }
                  if (datetime.day) {
                    scheduledDate.day = datetime.day;
                  }
                }
              "
            >
              <template #leading>
                <UPopover :reference="inputScheduleDate?.inputsRef[3]?.$el">
                  <UButton
                    color="neutral"
                    variant="link"
                    icon="i-lucide-calendar"
                    aria-label="Select a date"
                    class="px-0"
                  />
                  <template #content>
                    <UCalendar
                      v-model="scheduledDate"
                      class="p-2"
                      :min-value="today(getLocalTimeZone())"
                      @update:model-value="
                        (date) => {
                          if (
                            scheduledAt !== null &&
                            scheduledAt.year === date.year &&
                            scheduledAt.month === date.month &&
                            scheduledAt.day === date.day
                          ) {
                            return;
                          }
                          const tz = getLocalTimeZone();
                          scheduledAt = now(tz);
                          scheduledAt.year = date.year;
                          scheduledAt.month = date.month;
                          scheduledAt.day = date.day;
                          const _today = now(tz);
                          if (
                            scheduledAt.year === _today.year &&
                            scheduledAt.month === _today.month &&
                            scheduledAt.day === _today.day &&
                            scheduledAt.hour === _today.hour
                          ) {
                            scheduledAt = scheduledAt.add({ hours: 1 });
                          }
                        }
                      "
                    />
                  </template>
                </UPopover>
              </template>
              <template v-if="scheduledAt !== null" #trailing>
                <UButton
                  color="neutral"
                  variant="link"
                  icon="i-lucide-x"
                  aria-label="Clear selected date"
                  @click="
                    scheduledAt = null;
                    scheduledDate = null;
                  "
                />
              </template>
            </UInputDate>
          </UFormField>
          <UAlert title="Monitor" color="neutral" class="mt-8">
            <template #leading>
              <USwitch
                :model-value="false"
                @update:model-value="
                  (value) => {
                    repeatIn = value ? 1 : null;
                    repeatTimeUnit = value ? 'Days' : null;
                  }
                "
              />
            </template>
            <template v-if="repeatIn !== null" #description>
              <div class="flex items-center gap-2">
                <span>Run this scan each</span
                ><UInput
                  v-model="repeatIn"
                  type="number"
                  min="1"
                  class="w-20"
                />
                <USelect
                  v-model="repeatTimeUnit"
                  :items="utils.timeUnitOptions"
                  class="w-32"
                />
              </div>
            </template>
          </UAlert>
        </template>
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
import { today, now, getLocalTimeZone } from "@internationalized/date";

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
      description: "Tool or process to run",
      icon: "i-lucide-terminal",
    });
  }
  items.push({
    title: "Intensity",
    icon: "i-lucide-database-zap",
  });
  if (wordlistOptions.value.length > 0) {
    items.push({
      title: "Wordlists",
      icon: "i-mdi-file-word",
    });
  }
  if (inputTechnologyOptions.value.length > 0) {
    items.push({
      title: "Technologies",
      description: "Provide input parameters",
      icon: "i-lucide-code",
    });
  }
  if (inputVulnerabilityOptions.value.length > 0) {
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
const inputScheduleDate = useTemplateRef("inputScheduleDate");
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
const minIntensity = ref(1);
const maxIntensity = ref(5);
const wordlists = ref([]);
const wordlistOptions = ref([]);
const requiredWordlist = ref(false);
const inputTechnologies = ref([]);
const inputTechnologyOptions = ref([]);
const requiredInputTechnology = ref(false);
const inputVulnerabilities = ref([]);
const inputVulnerabilityOptions = ref([]);
const requiredInputVulnerability = ref(false);
const scheduledDate = ref(null);
const scheduledAt = ref(null);
const repeatIn = ref(null);
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
    genericApi.get(`tools/${tool.value}/`).then((response) => {
      // TODO: Test this. Assumes intensities are sorted, and assumes the step between all of them is 1
      minIntensity.value = response.intensities[0].value;
      maxIntensity.value =
        response.intensities[response.intensities.length - 1].value;
    });
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
    minIntensity.value = 1;
    maxIntensity.value = 5;
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
  genericApi.list("wordlists/", {}, true).then((response) => {
    wordlistOptions.value = response.items;
  });
}

function validate(): FormError[] {
  // TODO: Return FormErrors and test if this is working
  if (
    project.value &&
    target.value &&
    (process.value || (tool.value && configuration.value)) &&
    intensity.value &&
    (wordlists.value.length > 0 || !requiredWordlist.value) &&
    (inputTechnologies.value.length > 0 || !requiredInputTechnology.value) &&
    (inputVulnerabilities.value.length > 0 ||
      !requiredInputVulnerability.value) &&
    (!periodicMonitoring.value ||
      (periodicMonitoring.value && repeatIn.value && repeatTimeUnit.value))
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
        scheduled_at: scheduledAt.value.toString(),
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
