<template>
  <BaseDialog
    title="Scan"
    :loading="loading"
    width="1000"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <v-form v-model="valid" @submit.prevent="submit()">
      <v-stepper ref="stepper" v-model="step" editable flat>
        <v-stepper-header>
          <v-stepper-item
            v-if="project === null || target === null"
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
            v-if="(selectedProcess || selectedTool) && intensities.length > 1"
            title="Intensity"
            :value="2"
            icon="mdi-volume-high mdi-18px"
            edit-icon="mdi-volume-high mdi-18px"
            :color="step === 2 ? 'red' : undefined"
          />
          <v-stepper-item
            v-if="
              (selectedProcess && selectedProcess.wordlists.supported) ||
              (selectedTool && selectedTool.wordlists.supported)
            "
            title="Wordlists"
            :value="3"
            icon="mdi-file-word-box mdi-18px"
            edit-icon="mdi-file-word-box mdi-18px"
            :color="step === 3 ? 'red' : undefined"
          />
          <v-stepper-item
            v-if="selectedTool && selectedTool.require_input_technology"
            title="Technologies"
            :value="4"
            :icon="`${enums.findings.Technology.icon} mdi-18px`"
            :edit-icon="`${enums.findings.Technology.icon} mdi-18px`"
            :color="step === 4 ? 'red' : undefined"
          />
          <v-stepper-item
            v-if="selectedTool && selectedTool.require_input_vulnerability"
            title="Vulnerabilities"
            :value="5"
            :icon="`${enums.findings.Vulnerability.icon} mdi-18px`"
            :edit-icon="`${enums.findings.Vulnerability.icon} mdi-18px`"
            :color="step === 5 ? 'red' : undefined"
          />
          <v-stepper-item
            title="Schedule"
            :value="6"
            icon="mdi-timer mdi-18px"
            edit-icon="mdi-timer mdi-18px"
            :color="step === 6 ? 'red' : undefined"
          />
          <v-stepper-item
            title="Monitor"
            :value="7"
            icon="mdi-reload mdi-18px"
            edit-icon="mdi-reload mdi-18px"
            :color="step === 7 ? 'red' : undefined"
          />
        </v-stepper-header>
        <v-stepper-window>
          <v-container fluid>
            <v-stepper-window-item transition="fab-transition">
              <v-row v-if="project === null" justify="center" dense>
                <v-col cols="10">
                  <BaseAutocomplete
                    v-model="selectedProject"
                    clearable
                    density="comfortable"
                    variant="outlined"
                    label="Project"
                    :collection="projects"
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
                  <BaseAutocomplete
                    v-model="selectedTargets"
                    clearable
                    chips
                    density="comfortable"
                    variant="outlined"
                    label="Targets"
                    :collection="targets"
                    item-title="target"
                    return-object
                    :disabled="selectedProject === null"
                    multiple
                    :rules="[(t) => t.length > 0 || 'Target is required']"
                    validate-on="input"
                    @click:clear="allTargets = false"
                    @update:model-value="
                      allTargets = targets.length === selectedTargets.length
                    "
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
                  </BaseAutocomplete>
                </v-col>
              </v-row>
            </v-stepper-window-item>
            <v-stepper-window-item transition="fab-transition">
              <v-row
                :justify="tool === null ? 'space-between' : 'center'"
                dense
              >
                <v-col v-if="tool === null" align-self="center" cols="6">
                  <BaseAutocomplete
                    v-model="selectedProcess"
                    icon="mdi-robot-angry"
                    clearable
                    density="comfortable"
                    variant="outlined"
                    label="Process"
                    :collection="processes"
                    item-title="name"
                    return-object
                    :rules="[
                      (p) =>
                        p !== null ||
                        selectedTool !== null ||
                        'Process or tool is required',
                    ]"
                    validate-on="blur"
                    @update:model-value="selectProcess()"
                  />
                </v-col>
                <v-col align-self="center" :cols="tool !== null ? '11' : '6'">
                  <BaseAutocomplete
                    v-model="selectedTool"
                    clearable
                    icon="mdi-rocket"
                    density="comfortable"
                    variant="outlined"
                    label="Tool"
                    :collection="tools"
                    item-title="name"
                    return-object
                    :disabled="tool !== null"
                    :rules="[
                      (t) =>
                        t !== null ||
                        selectedProcess !== null ||
                        'Tool or process is required',
                    ]"
                    validate-on="blur"
                    @update:model-value="selectTool()"
                  >
                    <template
                      v-if="
                        selectedTool !== null && selectedTool.reference !== null
                      "
                      #append
                    >
                      <BaseButton :link="selectedTool.reference" new-tab hide />
                    </template>
                  </BaseAutocomplete>
                  <BaseAutocomplete
                    v-if="selectedTool !== null"
                    v-model="selectedConfiguration"
                    class="mt-5"
                    clearable
                    density="comfortable"
                    variant="outlined"
                    label="Configuration"
                    :collection="
                      selectedTool ? selectedTool.configurations : []
                    "
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
            </v-stepper-window-item>
            <v-stepper-window-item transition="fab-transition">
              <v-row justify="center" dense>
                <v-col cols="10">
                  <BaseAutocomplete
                    v-model="intensity"
                    icon="mdi-volume-high"
                    density="comfortable"
                    variant="outlined"
                    label="Intensity"
                    :collection="intensities"
                    item-title="name"
                    :color="intensity ? intensity.color : undefined"
                    return-object
                    :rules="[(i) => !!i || 'Intensity is required']"
                    validate-on="input"
                  />
                </v-col>
              </v-row>
            </v-stepper-window-item>
            <v-stepper-window-item transition="fab-transition">
              <v-row justify="center" dense>
                <v-col cols="6">
                  <BaseAutocomplete
                    v-model="wordlistFilter"
                    clearable
                    chips
                    multiple
                    density="comfortable"
                    variant="outlined"
                    label="Filter by type"
                    :definition="enums.wordlists"
                    prepend-inner-icon="mdi-routes"
                    @update:model-value="
                      selectedWordlists = [];
                      allWordlists = false;
                      getWordlists();
                    "
                  />
                </v-col>
              </v-row>
              <v-row>
                <BaseAutocomplete
                  v-model="selectedWordlists"
                  clearable
                  density="comfortable"
                  variant="outlined"
                  label="Wordlists"
                  :collection="wordlists"
                  item-title="name"
                  return-object
                  multiple
                  chips
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
                  @update:model-value="
                    allWordlists = wordlists.length === selectedWordlists.length
                  "
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
                </BaseAutocomplete>
              </v-row>
            </v-stepper-window-item>

            <!-- TODO: Add input parameters form to task dialog -->
            <v-stepper-window-item transition="fab-transition">
              <v-form
                v-model="validTechnology"
                @submit.prevent="submitTechnology()"
              >
                <v-row justify="space-around" dense>
                  <v-col cols="5">
                    <v-text-field
                      v-model="technologyName"
                      class="mt-2"
                      label="Technology"
                      variant="outlined"
                      :rules="[
                        (n) => !!n || 'Name is required',
                        (n) => validate.name.test(n) || 'Invalid name value',
                      ]"
                      validate-on="input"
                    />
                  </v-col>
                  <v-col cols="5">
                    <v-text-field
                      v-model="technologyVersion"
                      class="mt-2"
                      label="Version"
                      variant="outlined"
                      :rules="[
                        (v) =>
                          !v ||
                          validate.name.test(v) ||
                          'Invalid version value',
                      ]"
                      validate-on="input"
                    />
                  </v-col>
                  <v-col cols="1">
                    <BaseButton
                      class="mt-2"
                      type="submit"
                      icon="mdi-plus-circle"
                      icon-color="green"
                      size="x-large"
                      autofocus
                      tooltip="Add technology"
                    />
                  </v-col>
                </v-row>
              </v-form>
              <v-row justify="center">
                <v-chip-group v-model="selectedTechnologies" multiple>
                  <v-chip
                    v-for="technology in createdTechnologies"
                    :key="technology.id"
                    :value="technology.id"
                    :text="
                      technology.version
                        ? `${technology.name} ${technology.version}`
                        : technology.name
                    "
                    variant="outlined"
                    filter
                  />
                  <v-chip
                    v-for="technology in technologies"
                    :key="technology.id"
                    :value="technology.id"
                    :text="
                      technology.version
                        ? `${technology.name} ${technology.version}`
                        : technology.name
                    "
                    variant="outlined"
                    filter
                  />
                </v-chip-group>
              </v-row>
            </v-stepper-window-item>
            <v-stepper-window-item transition="fab-transition" />

            <v-stepper-window-item transition="fab-transition">
              <v-row justify="center" class="mb-5" dense>
                <v-col cols="10">
                  <v-alert
                    class="text-center"
                    color="info"
                    icon="$info"
                    variant="tonal"
                    text="You can schedule the execution at the best moment for you and your targets"
                  />
                </v-col>
              </v-row>
              <v-row justify="space-around" dense>
                <v-col cols="5">
                  <v-text-field
                    v-model="scheduledDate"
                    :model-value="
                      scheduledDate !== undefined && scheduledDate !== null
                        ? scheduledDate.toDateString()
                        : null
                    "
                    :active="dateMenu"
                    label="Date"
                    prepend-inner-icon="mdi-calendar"
                    variant="outlined"
                    readonly
                  >
                    <v-menu
                      v-model="dateMenu"
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
                <v-col cols="5">
                  <v-text-field
                    v-model="scheduledTime"
                    :active="timeMenu"
                    label="Time"
                    prepend-inner-icon="mdi-clock-outline"
                    variant="outlined"
                    readonly
                  >
                    <v-menu
                      v-model="timeMenu"
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
            </v-stepper-window-item>
            <v-stepper-window-item transition="fab-transition">
              <v-row justify="center" class="mb-5" dense>
                <v-col cols="11">
                  <v-alert
                    class="text-center"
                    color="info"
                    icon="$info"
                    variant="tonal"
                    text="Configure how often you want to execute this scan to monitor your targets"
                  />
                </v-col>
              </v-row>
              <v-row justify="space-around" dense>
                <v-col cols="4">
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
                <v-col cols="5">
                  <BaseAutocomplete
                    v-model="timeUnit"
                    variant="outlined"
                    label="Time unit"
                    :collection="enums.timeUnits"
                  />
                </v-col>
              </v-row>
            </v-stepper-window-item>
          </v-container>
        </v-stepper-window>
        <v-stepper-actions
          @click:next="stepper.next()"
          @click:prev="stepper.prev()"
        />
      </v-stepper>
      <UtilsSubmit
        v-if="!loading"
        text="Execute"
        :autofocus="false"
        :disabled="!isValid()"
        prepend-icon="mdi-play"
      />
      <UtilsPercentage
        v-if="loading"
        :total="selectedTargets.length"
        :progress="progress"
      />
    </v-form>
  </BaseDialog>
</template>

<script setup lang="ts">
import { VTimePicker } from "vuetify/labs/VTimePicker";
import { VNumberInput } from "vuetify/labs/VNumberInput";
const props = defineProps({
  project: { type: Object, required: false, default: null },
  target: { type: Object, required: false, default: null },
  process: { type: Object, required: false, default: null },
  tool: { type: Object, required: false, default: null },
  configuration: { type: Object, required: false, default: null },
});
const emit = defineEmits(["reload", "closeDialog"]);
const api = useApi("/api/tasks/", true, "Task");
const enums = useEnums();
const route = useRoute();
const router = useRouter();
const validate = useValidation();

const loading = ref(false);
const valid = ref(true);
const stepper = ref(null);
const step = ref(props.target ? 1 : 0);
const allTargets = ref(false);
const allWordlists = ref(false);
const timeMenu = ref(false);
const dateMenu = ref(false);
const progress = ref(0);

const technologyApi = useApi(
  "/api/parameters/technologies/",
  true,
  "Technology",
);
const validTechnology = ref(true);
const technologyName = ref(null);
const technologyVersion = ref(null);

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
const wordlistFilter = ref(Object.keys(enums.wordlists));
const selectedWordlists = ref([]);
const createdTechnologies = ref([]);
const technologies = ref([]);
const selectedTechnologies = ref([]);
const vulnerabilities = ref([]);
const selectedVulnerabilities = ref([]);
const scheduledDate = ref(null);
const scheduledTime = ref(null);
const monitor = ref(null);
const timeUnit = ref("Days");

if (!selectedProject.value) {
  useApi("/api/projects/", true, "Project")
    .list({}, true)
    .then((response) => (projects.value = response.items));
} else if (selectedTargets.value.length === 0) {
  selectProject();
}
if (
  !selectedProcess.value &&
  !selectedTool.value &&
  !selectedConfiguration.value
) {
  useApi("/api/processes/", true, "Process")
    .list({}, true)
    .then((response) => (processes.value = response.items));
  useApi("/api/tools/", true, "Tool")
    .list({}, true)
    .then((response) => (tools.value = response.items));
} else if (selectedTool.value) {
  selectTool();
} else if (selectedProcess.value) {
  selectProcess();
}

function selectProject(): void {
  allTargets.value = false;
  selectedTargets.value = [];
  useApi("/api/targets/", true, "Target")
    .list({ project: selectedProject.value.id }, true)
    .then((response) => (targets.value = response.items));
}

function selectTool(): void {
  if (selectedTool.value) {
    selectedProcess.value = null;
    selectedConfiguration.value = null;
    useApi("/api/configurations/", true, "Configuration")
      .list({ tool: selectedTool.value.id, default: true })
      .then((response) => (selectedConfiguration.value = response.items[0]));
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
    if (selectedTool.value.require_input_technology) {
      getTechnologies();
    }
    if (selectedTool.value.require_input_vulnerability) {
      getVulnerabilities();
    }
  }
}

function selectProcess(): void {
  if (selectedProcess.value) {
    selectedTool.value = null;
    selectedConfiguration.value = null;
    intensities.value = Object.entries(enums.intensities).map(([k, v]) => {
      v.name = k;
      return v;
    });
    intensity.value = Object.assign(
      {},
      { name: "Normal" },
      enums.intensities.Normal,
    );
    if (
      wordlists.value.length === 0 &&
      selectedProcess.value.wordlists.supported
    ) {
      getWordlists();
    }
  }
}

function getWordlists(): void {
  useApi("/api/wordlists/", true, "Wordlist")
    .list(wordlistFilter.value ? { type: wordlistFilter.value } : {}, true)
    .then((response) => (wordlists.value = response.items));
}

function getTechnologies(): void {
  technologyApi
    .list({}, true)
    .then((response) => (technologies.value = response.items));
}

function getVulnerabilities(): void {
  useApi("/api/parameters/vulnerabilities/", true, "Vulnerability")
    .list({}, true)
    .then((response) => (vulnerabilities.value = response.items));
}

function getMinDate(): string {
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

function getMinTime(): string {
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

function isValid(): boolean {
  return (
    selectedTargets.value.length > 0 &&
    (selectedProcess.value || selectedConfiguration.value) &&
    intensity.value &&
    (!(selectedProcess.value ? selectedProcess.value : selectedTool.value)
      .wordlists.required ||
      selectedWordlists.value.length > 0)
  );
}

function submitTechnology(): void {
  if (validTechnology.value) {
    technologyApi
      .create({ name: technologyName.value, version: technologyVersion.value })
      .then((response) => {
        if (
          technologies.value.filter((t) => t.id === response.id).length === 0
        ) {
          createdTechnologies.value.push(response);
        }
        if (!selectedTechnologies.value.includes(response.id)) {
          selectedTechnologies.value.push(response.id);
        }
        technologyName.value = null;
        technologyVersion.value = null;
      });
  }
}

function submit(): void {
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
    if (selectedTechnologies.value.length > 0) {
      body.input_technologies = selectedTechnologies.value;
    }
    let errors = 0;
    loading.value = true;
    progress.value = 0;
    for (const target of selectedTargets.value) {
      body.target_id = target.id;
      api
        .create(body)
        .then((response) => {
          progress.value++;
          if (errors + progress.value === selectedTargets.value.length) {
            loading.value = false;
            if (
              selectedTargets.value.length > 1 ||
              (scheduledDate.value && scheduledTime.value)
            ) {
              if (/^\/projects\/[\d]+\/scans$/.test(route.path)) {
                emit("reload");
              } else {
                router.push({
                  path: `/projects/${selectedProject.value.id}/scans`,
                });
              }
            } else {
              router.push({
                path: `/projects/${selectedProject.value.id}/scans/${response.id}`,
              });
            }
          }
        })
        .catch(() => {
          errors++;
          if (errors + progress.value === selectedTargets.value.length) {
            loading.value = false;
            if (progress.value > 0) {
              if (/^\/projects\/[\d]+\/scans$/.test(route.path)) {
                emit("reload");
              } else {
                router.push({
                  path: `/projects/${selectedProject.value.id}/scans`,
                });
              }
            }
          }
        });
    }
  }
}
</script>
