<template>
  <DialogDefault
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
            <!-- TODO: Allow association to Task from here -->
            <v-autocomplete
              v-model="selectedTarget"
              class="text-upper"
              auto-select-first
              density="comfortable"
              variant="outlined"
              label="Target"
              :items="targets"
              item-title="target"
              return-object
              validate-on="input"
              prepend-icon="mdi-target"
            />
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
              :items="Object.keys(enums.reports)"
              validate-on="input"
              :prepend-icon="format ? enums.reports[format].icon : undefined"
            >
              <template #item="{ props, item }">
                <v-list-item
                  v-bind="props"
                  :title="item.raw.toUpperCase()"
                  :prepend-icon="enums.reports[item.raw].icon"
                />
              </template>
              <template #selection="{ item, index }">
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
              <!-- todo: Look for other cases where this is useful -->
              <template #chip="{ props, item }">
                <v-chip
                  v-bind="props"
                  :class="
                    item.raw === 'osint' ? 'text-uppercase' : 'text-capitalize'
                  "
                  :prepend-icon="enums.findings[item.raw.toLowerCase()].icon"
                  :text="item.raw"
                />
              </template>
              <template #item="{ props, item }">
                <v-list-item
                  v-bind="props"
                  :title="
                    item.raw === 'osint'
                      ? item.raw.toUpperCase()
                      : `${item.raw.charAt(0).toUpperCase()}${item.raw.slice(1)}`
                  "
                  :prepend-icon="enums.findings[item.raw.toLowerCase()].icon"
                />
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>
      </v-conatiner>
      <ButtonSubmit text="Create" :autofocus="false" class="mt-5" />
    </v-form>
  </DialogDefault>
</template>
<!-- TODO: Move component_type/entity model to entity/component_type -->
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

const enums = useEnums();
const api = useApi("/api/reports/", true, "Report");
const loading = ref(false);
const valid = ref(true);

const targets = ref([]);
const selectedTarget = ref(props.target !== null ? props.target : null);
if (selectedTarget.value === null && props.task === null) {
  searchTargets();
}

const onlyTruePositives = ref(true);
const findingTypes = ref(Object.keys(enums.findings));
const format = ref("pdf");

function searchTargets() {
  useApi("/api/targets/", true, "Target")
    .list({ project: props.parameters.project }, true)
    .then((response) => (targets.value = response.items));
}

function submit() {
  loading.value = true;
  api
    .create({
      project: parseInt(props.parameters.project),
      target: selectedTarget.value ? selectedTarget.value.id : null,
      task: props.task ? props.task.id : null,
      format: format.value,
      only_true_positives: onlyTruePositives.value,
      finding_types: findingTypes.value.map(function (item) {
        return item === "osint"
          ? item.toUpperCase()
          : `${item.charAt(0).toUpperCase()}${item.slice(1)}`;
      }),
    })
    .then((response) => {
      loading.value = false;
      emit("completed", response);
    })
    .catch(() => (loading.value = false));
}
</script>
