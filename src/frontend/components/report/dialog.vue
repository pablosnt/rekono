<template>
  <Dialog
    title="Create Report"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <v-form v-model="valid" class="mt-3" @submit.prevent="submit()">
      <v-conatiner fluid>
        <v-row v-if="target === null && task === null" justify="center" dense>
          <v-col cols="11">
            <v-autocomplete
              v-model="selectedTarget"
              auto-select-first
              density="comfortable"
              variant="outlined"
              label="Target"
              :items="targets"
              item-title="target"
              return-object
              validate-on="input"
              prepend-icon="mdi-target"
              @update:model-value="searchTasks()"
            />
          </v-col>
        </v-row>
        <v-row v-if="task === null" justify="center" dense>
          <v-col cols="11">
            <v-autocomplete
              v-model="selectedTask"
              :disabled="!selectedTarget"
              auto-select-first
              density="comfortable"
              variant="outlined"
              label="Task"
              :items="tasks"
              return-object
              validate-on="input"
              prepend-icon="mdi-play-network"
            >
              <template #item="{ props: taskProps, item }">
                <v-list-item v-bind="taskProps" :title="item.title" />
              </template>
              <template #selection="{ item }">
                <p>{{ item.title }}</p>
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>
        <v-row justify="space-around" dense>
          <v-col cols="5">
            <v-autocomplete
              v-model="format"
              auto-select-first
              density="comfortable"
              variant="outlined"
              label="Format"
              :items="Object.keys(enums.reportFormats)"
              validate-on="input"
              :prepend-icon="
                format ? enums.reportFormats[format].icon : undefined
              "
            >
              <template #item="{ props: formatProps, item }">
                <v-list-item
                  v-bind="formatProps"
                  :title="item.raw.toUpperCase()"
                  :prepend-icon="enums.reportFormats[item.raw].icon"
                />
              </template>
              <template #selection="{ item }">
                <p>{{ item.raw.toUpperCase() }}</p>
              </template>
            </v-autocomplete>
          </v-col>
          <v-col cols="4">
            <v-switch
              v-model="onlyTruePositives"
              color="green"
              label="Only True Positives"
            />
          </v-col>
        </v-row>
        <v-row justify="center" dense>
          <v-col cols="11">
            <v-autocomplete
              v-model="findingTypes"
              :disabled="format === 'pdf'"
              auto-select-first
              density="comfortable"
              variant="outlined"
              label="Finding Types"
              :items="Object.keys(enums.findings)"
              :rules="[
                (f) => f.length > 0 || 'At least one finding type is required',
              ]"
              validate-on="input"
              prepend-icon="mdi-ladybug"
              multiple
              chips
              clearable
              closable-chips
            >
              <!-- TODO: Look for other cases where this is useful -->
              <template #chip="{ props: findingProps, item }">
                <v-chip
                  v-bind="findingProps"
                  :prepend-icon="enums.findings[item.raw].icon"
                  :text="item.raw"
                />
              </template>
              <template #item="{ props: findingProps, item }">
                <v-list-item
                  v-bind="findingProps"
                  :title="
                    item.raw === 'osint'
                      ? item.raw.toUpperCase()
                      : `${item.raw.charAt(0).toUpperCase()}${item.raw.slice(1)}`
                  "
                  :prepend-icon="enums.findings[item.raw].icon"
                />
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>
      </v-conatiner>
      <UtilsButtonSubmit text="Create" :autofocus="false" class="mt-5" />
    </v-form>
  </Dialog>
</template>

<script setup lang="ts">
const props = defineProps({
  parameters: {
    type: Object,
    required: false,
    default: null,
  },
  target: {
    type: Object,
    required: false,
    default: null,
  },
  task: {
    type: Object,
    required: false,
    default: null,
  },
});
const emit = defineEmits(["closeDialog", "completed"]);

const taskUtils = useTasks();
const enums = useEnums();
const api = useApi("/api/reports/", true, "Report");
const loading = ref(false);
const valid = ref(true);

const targets = ref([]);
const selectedTarget = ref(props.target !== null ? props.target : null);
if (selectedTarget.value === null && props.task === null) {
  searchTargets();
}

const tasks = ref([]);
const selectedTask = ref(props.task !== null ? props.task : null);
if (selectedTask.value === null && selectedTarget.value !== null) {
  searchTasks();
}

const onlyTruePositives = ref(true);
const findingTypes = ref(Object.keys(enums.findings));
const format = ref("pdf");

function searchTargets(): void {
  useApi("/api/targets/", true)
    .list({ project: props.parameters.project }, true)
    .then((response) => (targets.value = response.items));
}

function searchTasks(): void {
  useApi("/api/tasks/", true)
    .list({ target: selectedTarget.value.id }, true)
    .then((response) => {
      tasks.value = response.items;
      for (const task of tasks.value) {
        taskUtils.getTitle(task);
      }
    });
}

function submit(): void {
  loading.value = true;
  api
    .create({
      project: parseInt(props.parameters.project),
      target: selectedTarget.value ? selectedTarget.value.id : null,
      task: props.task ? props.task.id : null,
      format: format.value,
      only_true_positives: onlyTruePositives.value,
      finding_types: findingTypes.value,
    })
    .then((response) => {
      loading.value = false;
      emit("completed", response);
    })
    .catch(() => (loading.value = false));
}
</script>
