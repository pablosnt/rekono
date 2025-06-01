<template>
  <v-stepper
    v-model="stage"
    editable
    alt-labels
    hide-actions
    flat
    @update:model-value="
      tool = null;
      configurations = [];
      getSteps();
      getTools();
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
          <v-col cols="3">
            <BaseAutocomplete
              v-model="tool"
              clearable
              hide-details
              variant="outlined"
              label="Tool"
              icon="mdi-rocket"
              icon-color="red"
              :collection="tools"
              :title="(tool) => tool.name"
              return-object
              @update:model-value="
                getSteps();
                tool !== null ? getConfigurations() : (configurations = []);
              "
            />
          </v-col>
        </v-row>
      </v-container>
      <v-empty-state
        v-if="configurations.length === 0 && steps.length === 0"
        icon="mdi-rocket"
        title="There are no steps. Choose the tool and configuration you want to run as part of this process"
      />
      <v-row justify="space-around">
        <v-col v-if="steps.length > 0" cols="4">
          <template v-for="step in steps" :key="step.id">
            <v-banner
              :text="
                tool === null
                  ? step.configuration.tool.name +
                    ': ' +
                    step.configuration.name
                  : step.configuration.name
              "
              :stacked="false"
            >
              <template #prepend>
                <BaseButton
                  v-if="configurations.length === 0"
                  class="mt-5"
                  :avatar="step.configuration.tool.icon"
                  :icon="
                    step.configuration.tool.icon === null
                      ? 'mdi-rocket'
                      : undefined
                  "
                  icon-color="red"
                  :link="step.configuration.tool.reference"
                  new-tab
                />
              </template>
              <template #actions>
                <v-switch
                  color="red"
                  :model-value="true"
                  @click="removeStep(step.id)"
                />
              </template>
            </v-banner>
          </template>
        </v-col>
        <v-col v-if="configurations.length > 0" cols="4">
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
const enums = useEnums();
const api = useApi("/api/steps/", true, "Step");
const toolApi = useApi("/api/tools/", true, "Tool");
const configurationApi = useApi("/api/configurations/", true, "Configuration");
const steps = ref([]);
const tools = ref([]);
const tool = ref(null);
const configurations = ref([]);
const stages = ref(Object.keys(enums.stages));
const currentStages = props.process.steps.map(
  (step) => step.configuration.stage,
);
const stage = ref(null);
if (props.process.steps.length > 0) {
  stage.value = stages.value.indexOf(
    stages.value.filter((s) => currentStages.includes(s))[0],
  );
  getSteps();
}
getTools();

function getTools(): void {
  if (stage.value !== null) {
    toolApi
      .list({ stage: enums.stages[stages.value[stage.value]].id })
      .then((response) => (tools.value = response.items));
  }
}

function getSteps(): void {
  const params = {
    stage: enums.stages[stages.value[stage.value]].id,
    process: props.process.id,
  };
  if (tool.value) {
    params.tool = tool.value.id;
  }
  api.list(params, true).then((response) => (steps.value = response.items));
}

function removeStep(id: number): void {
  api.remove(id).then(() => {
    getSteps();
    getConfigurations();
  });
}

function getConfigurations(): void {
  if (tool.value) {
    configurationApi
      .list({
        stage: enums.stages[stages.value[stage.value]].id,
        tool: tool.value.id,
        no_process: props.process.id,
      })
      .then((response) => (configurations.value = response.items));
  }
}
</script>
