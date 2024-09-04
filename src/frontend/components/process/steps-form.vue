<template>
  <v-stepper
    v-model="stage"
    editable
    alt-labels
    hide-actions
    flat
    @update:model-value="
      tool = null;
      getSteps();
      getTools();
      getConfigurations();
    "
  >
    <v-stepper-header>
      <template v-for="s in stages" :key="s">
        <v-divider v-if="s !== stages[0]" />
        <v-stepper-item
          :title="s"
          :color="enums.stages[s].color"
          :icon="enums.stages[s].icon"
          :edit-icon="enums.stages[s].icon"
        />
      </template>
    </v-stepper-header>
    <v-stepper-window>
      <v-container fluid>
        <v-row justify="center" dense>
          <v-col cols="5">
            <v-autocomplete
              v-model="tool"
              clearable
              auto-select-first
              hide-details
              density="comfortable"
              variant="outlined"
              label="Tool"
              :items="tools"
              item-title="name"
              return-object
              @update:model-value="
                getSteps();
                getConfigurations();
              "
            >
              {{ tool }}
              <template v-if="tool !== null && tool.icon !== null" #prepend>
                <v-avatar :image="tool.icon" />
              </template>
              <template v-if="tool !== null && tool.reference !== null" #append>
                <UtilsButtonLink :link="tool.reference" />
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>
      </v-container>

      <v-empty-state
        v-if="configurations.length === 0 && process.steps.length === 0"
        icon="mdi-rocket"
        title="There are no steps in this process yet"
      />

      <v-row
        :justify="
          configurations.length > 0 && steps.length > 0
            ? 'space-between'
            : 'center'
        "
        dense
      >
        <v-col v-if="steps.length > 0" cols="5">
          <template v-for="step in steps" :key="step.id">
            <v-banner
              :avatar="tool === null ? step.configuration.tool.icon : null"
              :text="
                tool === null
                  ? step.configuration.tool.name +
                    '  -  ' +
                    step.configuration.name
                  : step.configuration.name
              "
              :stacked="false"
            >
              <template #actions>
                <v-btn
                  v-if="configurations.length === 0"
                  hover
                  icon="mdi-close"
                  color="red"
                  @click="removeStep(step.id)"
                />
                <v-switch
                  v-if="configurations.length > 0"
                  color="red"
                  :model-value="true"
                  @click="removeStep(step.id)"
                />
                <UtilsButtonLink
                  v-if="configurations.length === 0"
                  :link="step.configuration.tool.reference"
                />
              </template>
            </v-banner>
          </template>
        </v-col>
        <v-col v-if="configurations.length > 0" cols="5">
          <template
            v-for="configuration in configurations"
            :key="configuration.id"
          >
            <v-banner :text="configuration.name" :stacked="false">
              <template #actions>
                <v-switch
                  v-if="configurations.length > 0"
                  color="red"
                  :model-value="false"
                  @click="
                    api
                      .create({
                        configuration_id: configuration.id,
                        process_id: process.id,
                      })
                      .then(() => {
                        getSteps();
                        getConfigurations();
                        emit('reload');
                      })
                  "
                />
              </template>
            </v-banner>
          </template>
        </v-col>
      </v-row>
    </v-stepper-window>
  </v-stepper>
</template>

<script setup lang="ts">
const props = defineProps({ process: Object });
const emit = defineEmits(["reload"]);
const enums = ref(useEnums());
const stages = ref(Object.keys(enums.value.stages));
const currentStages = props.process.steps.map(
  (step) => step.configuration.stage,
);
const stage = ref(
  props.process.steps.length > 0
    ? stages.value.indexOf(
        stages.value.filter((s) => currentStages.includes(s))[0],
      )
    : null,
);
function defaultParams() {
  return stage.value !== null
    ? { stage: enums.value.stages[stages.value[stage.value]].id }
    : {};
}

const toolApi = useApi("/api/tools/", true, "Tool");
const tools = ref([]);
const tool = ref(null);
function getTools() {
  if (stage.value !== null) {
    toolApi
      .list(defaultParams())
      .then((response) => (tools.value = response.items));
  }
}

const api = useApi("/api/steps/", true, "Step");
const steps = ref([]);
getSteps();
function getSteps() {
  const params = defaultParams();
  params.process = props.process.id;
  if (tool.value) {
    params.tool = tool.value.id;
  }
  api.list(params, true).then((response) => (steps.value = response.items));
}
function removeStep(id: number) {
  api.remove(id).then(() => {
    getSteps();
    getConfigurations();
    emit("reload");
  });
}

const configurationApi = useApi("/api/configurations/", true, "Configuration");
const configurations = ref([]);
function getConfigurations() {
  if (tool.value) {
    const params = defaultParams();
    params.tool = tool.value.id;
    params.no_process = props.process.id;
    configurationApi
      .list(params)
      .then((response) => (configurations.value = response.items));
  } else {
    configurations.value = [];
  }
}

getTools();
</script>
