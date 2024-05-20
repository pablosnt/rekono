<template>
  <v-form v-model="valid" @submit.prevent="submit()">
    <v-stepper ref="stepper" v-model="step" editable flat>
      <v-stepper-header>
        <v-stepper-item
          title="Target"
          :value="0"
          icon="mdi-target mdi-18px"
          edit-icon="mdi-target mdi-18px"
          :color="step === 0 ? 'red' : undefined"
        />
        <v-stepper-item
          v-if="process === null"
          title="Payload"
          :value="1"
          :subtitle="tool === null ? 'Process or Tool' : null"
          icon="mdi-spider mdi-18px"
          edit-icon="mdi-spider mdi-18px"
          :color="step === 1 ? 'red' : undefined"
        />
        <v-stepper-item
          title="Intensity"
          :value="2"
          icon="mdi-volume-high mdi-18px"
          edit-icon="mdi-volume-high mdi-18px"
          :color="step === 2 ? 'red' : undefined"
        />
        <v-stepper-item
          title="Wordlists"
          :disabled="
            (selectedProcess === null ||
              !selectedProcess.wordlists.supported) &&
            (selectedTool === null || !selectedTool.wordlists.supported)
          "
          :value="3"
          icon="mdi-file-word-box mdi-18px"
          edit-icon="mdi-file-word-box mdi-18px"
          :color="step === 3 ? 'red' : undefined"
        />
        <v-stepper-item
          title="Schedule"
          :value="4"
          icon="mdi-timer mdi-18px"
          edit-icon="mdi-timer mdi-18px"
          :color="step === 4 ? 'red' : undefined"
        />
        <v-stepper-item
          title="Monitor"
          :value="5"
          icon="mdi-reload mdi-18px"
          edit-icon="mdi-reload mdi-18px"
          :color="step === 5 ? 'red' : undefined"
        />
      </v-stepper-header>

      <v-stepper-window>
        <v-stepper-window-item transition="fab-transition">
          <v-container fluid>
            <v-row justify="center" dense>
              <v-col cols="10">
                <v-autocomplete
                  v-model="selectedProject"
                  clearable
                  auto-select-first
                  density="comfortable"
                  variant="outlined"
                  label="Project"
                  :items="projects"
                  item-title="name"
                  return-object
                  :rules="[(p) => !!p || 'Project is required']"
                  validate-on="input"
                  @update:model-value="selectProject()"
                />
              </v-col>
            </v-row>
            <v-row class="mt-3" justify="center" dense>
              <v-col cols="10">
                <v-autocomplete
                  v-model="selectedTargets"
                  clearable
                  chips
                  auto-select-first
                  density="comfortable"
                  variant="outlined"
                  label="Targets"
                  :items="targets"
                  item-title="target"
                  return-object
                  :disabled="selectedProject === null"
                  multiple
                  :rules="[(t) => t.length > 0 || 'Target is required']"
                  validate-on="input"
                  @click:clear="allTargets = false"
                >
                  <template #prepend>
                    <v-checkbox
                      v-model="allTargets"
                      label="All"
                      hide-details
                      @update:model-value="
                        (value) => (selectedTargets = value ? targets : [])
                      "
                    />
                  </template>
                </v-autocomplete>
              </v-col>
            </v-row>
          </v-container>
        </v-stepper-window-item>

        <v-stepper-window-item transition="fab-transition">
          <v-container class="fill-height" fluid>
            <v-row :justify="tool === null ? 'space-between' : 'center'" dense>
              <v-col v-if="tool === null" align-self="center" cols="4">
                <v-autocomplete
                  v-model="selectedProcess"
                  clearable
                  auto-select-first
                  density="comfortable"
                  variant="outlined"
                  label="Process"
                  :items="processes"
                  item-title="name"
                  return-object
                  :rules="[
                    (p) =>
                      p !== null ||
                      selectedConfiguration !== null ||
                      'Project is required',
                  ]"
                  validate-on="input"
                  @update:model-value="selectProcess()"
                />
              </v-col>
              <v-col align-self="center" :cols="tool !== null ? '10' : '6'">
                <v-autocomplete
                  v-model="selectedTool"
                  clearable
                  auto-select-first
                  density="comfortable"
                  variant="outlined"
                  label="Tool"
                  :items="tools"
                  item-title="name"
                  return-object
                  :disabled="tool !== null"
                  :rules="[
                    (t) =>
                      t !== null ||
                      selectedProcess !== null ||
                      'Tool is required',
                  ]"
                  validate-on="input"
                  @update:model-value="selectTool()"
                >
                  <template
                    v-if="selectedTool !== null && selectedTool.icon !== null"
                    #prepend
                  >
                    <v-avatar :image="selectedTool.icon" />
                  </template>
                  <template
                    v-if="
                      selectedTool !== null && selectedTool.reference !== null
                    "
                    #append
                  >
                    <v-btn
                      icon="mdi-open-in-new"
                      color="medium-emphasis"
                      variant="text"
                      target="_blank"
                      :href="selectedTool.reference"
                      hover
                    />
                  </template>
                </v-autocomplete>
                <v-autocomplete
                  v-model="selectedConfiguration"
                  class="mt-5"
                  clearable
                  auto-select-first
                  density="comfortable"
                  variant="outlined"
                  label="Configuration"
                  :items="selectedTool ? selectedTool.configurations : []"
                  :disabled="selectedTool === null"
                  item-title="name"
                  return-object
                  :rules="[
                    (c) =>
                      c !== null ||
                      selectedProcess !== null ||
                      'Configuration is required',
                  ]"
                  validate-on="input"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-stepper-window-item>

        <v-stepper-window-item transition="fab-transition">
          <v-container fluid>
            <v-row justify="center" dense>
              <v-col cols="10">
                <v-autocomplete
                  v-model="intensity"
                  auto-select-first
                  density="comfortable"
                  variant="outlined"
                  label="Intensity"
                  :items="intensities"
                  item-title="name"
                  :color="intensity ? intensity.color : undefined"
                  :disabled="
                    (selectedProcess === null && selectedTool === null) ||
                    (intensities.length === 1 && intensity)
                  "
                  return-object
                  :rules="[(i) => !!i || 'Intensity is required']"
                  validate-on="input"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-stepper-window-item>

        <v-stepper-window-item transition="fab-transition">
          <v-container fluid>
            <v-row justify="space-between" dense>
              <v-col cols="3">
                <v-autocomplete
                  v-model="wordlistFilter"
                  clearable
                  auto-select-first
                  density="comfortable"
                  variant="outlined"
                  label="Filter by type"
                  :items="enums.wordlists"
                  prepend-inner-icon="mdi-routes"
                  :disabled="selectedProcess === null && selectedTool === null"
                  @update:model-value="getWordlists()"
                />
              </v-col>
              <v-col cols="8">
                <v-autocomplete
                  v-model="selectedWordlists"
                  clearable
                  auto-select-first
                  density="comfortable"
                  variant="outlined"
                  label="Wordlists"
                  :items="wordlists"
                  item-title="name"
                  return-object
                  multiple
                  chips
                  :disabled="selectedProcess === null && selectedTool === null"
                  :rules="[
                    (w) =>
                      ((selectedProcess === null ||
                        !selectedProcess.wordlists.required) &&
                        (selectedTool === null ||
                          !selectedTool.wordlists.required)) ||
                      w.length > 0 ||
                      'Wordlist is required',
                  ]"
                  validate-on="input"
                  @click:clear="allWordlists = false"
                >
                  <template #prepend>
                    <v-checkbox
                      v-model="allWordlists"
                      label="All"
                      hide-details
                      @update:model-value="
                        (value) => (selectedWordlists = value ? wordlists : [])
                      "
                    />
                  </template>
                </v-autocomplete>
              </v-col>
            </v-row>
          </v-container>
        </v-stepper-window-item>

        <v-stepper-window-item transition="fab-transition">
          <v-container fluid>
            <v-row justify="center" class="mb-5" dense>
              <v-col cols="10">
                <v-alert
                  color="info"
                  icon="$info"
                  text="You can schedule the execution at the best moment for you and your targets"
                />
              </v-col>
            </v-row>
            <v-row justify="space-around" dense>
              <v-col cols="6">
                <v-text-field
                  v-model="scheduledDate"
                  :active="dateMenu"
                  label="Date"
                  prepend-inner-icon="mdi-calendar"
                  variant="underlined"
                  readonly
                >
                  <v-menu
                    v-model="dateMenu"
                    :close-on-content-click="false"
                    activator="parent"
                    transition="scale-transition"
                  >
                    <v-date-picker
                      v-if="dateMenu"
                      v-model="scheduledDate"
                      show-adjacent-months
                      :min="getMinDate()"
                    >
                      <template #actions>
                        <v-btn text="Clear" @click="scheduledDate = null" />
                      </template>
                    </v-date-picker>
                  </v-menu>
                </v-text-field>
              </v-col>
              <v-col cols="3">
                <v-text-field
                  v-model="scheduledTime"
                  :active="timeMenu"
                  label="Time"
                  prepend-inner-icon="mdi-clock-outline"
                  variant="underlined"
                  readonly
                >
                  <v-menu
                    v-model="timeMenu"
                    :close-on-content-click="false"
                    activator="parent"
                    transition="scale-transition"
                  >
                    <VTimePicker
                      v-if="timeMenu"
                      v-model="scheduledTime"
                      full-width
                      format="24hr"
                      :min="getMinTime()"
                      scrollable
                    >
                      <template #actions>
                        <v-btn text="Clear" @click="scheduledTime = null" />
                      </template>
                    </VTimePicker>
                  </v-menu>
                </v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-stepper-window-item>

        <v-stepper-window-item transition="fab-transition">
          <v-container fluid>
            <v-row justify="center" class="mb-5" dense>
              <v-col cols="11">
                <v-alert
                  color="info"
                  icon="$info"
                  text="Configure how often you want to monitor your targets by executing this task periodically"
                />
              </v-col>
            </v-row>
            <v-row justify="space-around" dense>
              <v-col cols="3">
                <VNumberInput
                  v-model="monitor"
                  control-variant="split"
                  label="Time"
                  inset
                  clearable
                  variant="outlined"
                  :max="60"
                  :min="1"
                />
              </v-col>
              <v-col cols="4">
                <v-autocomplete
                  v-model="timeUnit"
                  clearable
                  auto-select-first
                  density="comfortable"
                  variant="outlined"
                  label="Time unit"
                  :items="enums.timeUnits"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-stepper-window-item>
      </v-stepper-window>

      <v-stepper-actions
        @click:next="stepper.next()"
        @click:prev="stepper.prev()"
      />
    </v-stepper>

    <v-btn
      v-if="!loading"
      color="red"
      size="large"
      variant="tonal"
      text="Execute"
      type="submit"
      prepend-icon="mdi-play"
      block
      :disabled="!isValid()"
    />
    <v-progress-linear
      v-if="loading"
      v-model="progressPercentage"
      height="20"
      color="red"
    >
      <strong>{{ progressPercentage }}%</strong>
    </v-progress-linear>
  </v-form>
</template>

<script setup lang="ts">
import { VTimePicker } from "vuetify/labs/VTimePicker";
import { VNumberInput } from "vuetify/labs/VNumberInput";
const props = defineProps({
  api: {
    type: Object,
    required: false,
    default: useApi("/api/tasks/", true, "Task"),
  },
  project: {
    type: Object,
    required: false,
    default: null,
  },
  target: {
    type: Object,
    required: false,
    default: null,
  },
  process: {
    type: Object,
    required: false,
    default: null,
  },
  tool: {
    type: Object,
    required: false,
    default: null,
  },
});
const enums = useEnums();
const router = useRouter();
const valid = ref(true);
const stepper = ref(null);
const step = ref(0);
const allTargets = ref(false);
const allWordlists = ref(false);
const timeMenu = ref(false);
const dateMenu = ref(false);
const loading = ref(false);
const progress = ref(0);
const progressPercentage = computed(() => {
  return selectedTargets.value.length === 0
    ? 0
    : Math.ceil(progress.value / selectedTargets.value.length) * 100;
});

const projects = ref([]);
const selectedProject = ref(props.project ? props.project : null);
const targets = ref([]);
const selectedTargets = ref(props.target ? [props.target] : []);
const processes = ref([]);
const selectedProcess = ref(props.process ? props.process : null);
const tools = ref([]);
const selectedTool = ref(props.tool ? props.tool : null);
const selectedConfiguration = ref(null);
const intensities = ref([]);
const intensity = ref(null);
const wordlists = ref([]);
const wordlistFilter = ref(null);
const selectedWordlists = ref([]);
const scheduledDate = ref(null);
const scheduledTime = ref(null);
const monitor = ref(null);
const timeUnit = ref("Days");

if (!selectedProject.value) {
  useApi("/api/projects/", true, "Project")
    .list({}, true)
    .then((data) => (projects.value = data.items));
}
if (selectedTargets.value.length === 0 && selectedProject.value) {
  selectProject();
}
if (
  !selectedProcess.value &&
  !selectedTool.value &&
  !selectedConfiguration.value
) {
  useApi("/api/processes/", true, "Process")
    .list({}, true)
    .then((data) => (processes.value = data.items));
  useApi("/api/tools/", true, "Tool")
    .list({}, true)
    .then((data) => (tools.value = data.items));
} else if (selectedTool.value) {
  selectTool();
} else if (selectedProcess.value) {
  selectProcess();
}

function selectProject() {
  allTargets.value = false;
  selectedTargets.value = [];
  useApi("/api/targets/", true, "Target")
    .list({ project: selectedProject.value.id }, true)
    .then((data) => (targets.value = data.items));
}
function selectTool() {
  if (selectedTool.value) {
    selectedProcess.value = null;
    selectedConfiguration.value = null;
    useApi("/api/configurations/", true, "Configuration")
      .list({ tool: selectedTool.value.id, default: true })
      .then((data) => (selectedConfiguration.value = data.items[0]));
    intensity.value = null;
    intensities.value = selectedTool.value.intensities.map((item) => {
      const details = Object.assign(
        {},
        { name: item.value },
        enums.intensities[item.value],
      );
      if (item.value === "Normal") {
        intensity.value = details;
      }
      return details;
    });
    if (!intensity.value) {
      intensity.value = intensities.value[0];
    }
    if (
      wordlists.value.length === 0 &&
      selectedTool.value.wordlists.supported
    ) {
      getWordlists();
    }
  }
}
function selectProcess() {
  if (selectedProcess.value) {
    selectedTool.value = null;
    selectedConfiguration.value = null;
    defaultIntensities();
    if (
      wordlists.value.length === 0 &&
      selectedProcess.value.wordlists.supported
    ) {
      getWordlists();
    }
  }
}
function defaultIntensities() {
  intensities.value = Object.entries(enums.intensities).map(([k, v]) => {
    v.name = k;
    return v;
  });
  intensity.value = Object.assign(
    {},
    { name: "Normal" },
    enums.intensities.Normal,
  );
}
function getWordlists() {
  useApi("/api/wordlists/", true, "Wordlist")
    .list(wordlistFilter.value ? { type: wordlistFilter.value } : {}, true)
    .then((data) => (wordlists.value = data.items));
}
function getMinDate() {
  const date = new Date();
  if (scheduledTime.value) {
    const parsed = scheduledTime.value.split(":");
    if (
      date.getHours() > parsed[0] ||
      (date.getHours() === parsed[0] && date.getMinutes() > parsed[1])
    ) {
      date.setDate(date.getDate() + 1);
    }
  }
  return date.toISOString().split("T")[0];
}
function getMinTime() {
  const date = new Date();
  if (
    scheduledDate.value &&
    scheduledDate.value.toDateString() === date.toDateString()
  ) {
    date.setMinutes(date.getMinutes() + 30);
    return `${date.getHours()}:${date.getMinutes()}`;
  }
  return undefined;
}
function isValid() {
  return (
    selectedTargets.value.length > 0 &&
    (selectedProcess.value || selectedConfiguration.value) &&
    intensity.value &&
    (!(selectedProcess.value ? selectedProcess.value : selectedTool.value)
      .wordlists.required ||
      selectedWordlists.value.length > 0)
  );
}
function submit() {
  if (isValid()) {
    const body = { intensity: intensity.value.name };
    if (selectedProcess.value) {
      body.process_id = selectedProcess.value.id;
    }
    if (selectedConfiguration.value) {
      body.configuration_id = selectedConfiguration.value.id;
    }
    if (scheduledDate.value && scheduledTime.value) {
      const parsed = scheduledTime.value.split(":");
      scheduledDate.value.setHours(parsed[0], parsed[1]);
      body.scheduled_at = scheduledDate.value.toISOString();
    }
    if (monitor.value && timeUnit.value) {
      body.repeat_in = monitor.value;
      body.repeat_time_unit = timeUnit.value;
    }
    if (selectedWordlists.value.length > 0) {
      body.wordlists = selectedWordlists.value.map((w) => w.id);
    }
    let errors = 0;
    loading.value = true;
    progress.value = 0;
    for (let i = 0; i < selectedTargets.value.length; i++) {
      body.target_id = selectedTargets.value[i].id;
      api
        .create(body)
        .then((data) => {
          progress.value++;
          if (errors + progress.value === selectedTargets.value.length) {
            loading.value = false;
            if (selectedTargets.value.length > 1) {
              router.push({
                path: `/projects/${selectedProject.value.id}/tasks`,
              });
            } else {
              router.push({
                path: `/projects/${selectedProject.value.id}/tasks/${data.id}`,
              });
            }
          }
        })
        .catch(() => {
          errors++;
        });
    }
  }
}
</script>
