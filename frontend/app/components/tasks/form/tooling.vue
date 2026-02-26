<template>
  <div class="space-y-4 mx-auto mt-3">
    <UFormField
      v-if="!defaultTool && !defaultProcess"
      required
      label="Tooling"
      name="tooling"
    >
      <USelectMenu
        class="w-full"
        :icon="toolingIcon"
        :avatar="toolingAvatar"
        :items="
          toolOptions
            .map((tool) => ({
              value: tool.id,
              label: tool.name,
              description: 'Tool',
              avatar: tool.icon ? { src: tool.icon } : undefined,
            }))
            .concat(
              processOptions.map((process) => ({
                id: process.id,
                label: process.name,
                description: 'Process',
              })),
            )
        "
        :filter-fields="['label', 'description']"
        size="xl"
        @update:model-value="
          (value) => {
            if (value) {
              if (value.description === 'Tool') {
                onTool(value.value);
              } else {
                onProcess(value.value);
              }
            } else {
              onTool(undefined);
              onProcess(undefined);
              onConfiguration(undefined);
              configurationOptions = [];
              toolingIcon = 'i-lucide-terminal';
              toolingAvatar = undefined;
            }
          }
        "
      >
        <template #trailing>
          <UIcon
            v-if="!tool && !process"
            class="group-data-[state=open]:rotate-180 transition-transform duration-200"
            name="i-lucide-chevron-down"
          />
          <UButton
            v-else
            icon="i-lucide-x"
            variant="ghost"
            color="neutral"
            size="sm"
            @click="
              onTool(undefined);
              onProcess(undefined);
              onConfiguration(undefined);
              configurationOptions = [];
              toolingIcon = 'i-lucide-terminal';
              toolingAvatar = undefined;
            "
          />
        </template>
      </USelectMenu>
    </UFormField>
    <UFormField v-if="tool" required label="Configuration" name="configuration">
      <USelectMenu
        :model-value="configuration"
        class="w-full"
        :disabled="configurationOptions.length === 1"
        :items="configurationOptions"
        size="xl"
        value-key="id"
        label-key="name"
        @update:model-value="(value) => onConfiguration(value)"
      />
    </UFormField>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  api: typeof useApi;
  defaultTool: number | undefined;
  defaultConfiguration: number | undefined;
  defaultProcess: number | undefined;
}>();
const emit = defineEmits<{
  "update-tool": [newTool: number | undefined];
  "update-configuration": [newConfiguration: number | undefined];
  "update-process": [newProcess: number | undefined];
  "update-wordlist": [supported: boolean, required: boolean];
  "update-input-technology": [required: boolean];
  "update-input-vulnerability": [required: boolean];
  "update-intensity": [newMaxIntensity: number, newMinIntensity: number];
}>();

const backend = useBackend();
const toolingIcon = ref("i-lucide-terminal");
const toolingAvatar = ref(undefined);
const process = ref(props.defaultProcess);
const processOptions = ref([]);
const tool = ref(props.defaultTool);
const toolOptions = ref([]);
const configuration = ref(props.defaultConfiguration);
const defaultConfigurationObject = ref();
const configurationOptions = ref([]);
const minIntensity = ref(1);
const maxIntensity = ref(5);
const supportedWordlist = ref(false);
const requiredWordlist = ref(false);
const requiredInputTechnology = ref(false);
const requiredInputVulnerability = ref(false);

function loadTooling() {
  props.api.list("tools/", {}, true).then((response) => {
    toolOptions.value = response.items;
  });
  props.api.list("processes/", {}, true).then((response) => {
    processOptions.value = response.items;
  });
}

function restoreIntensityRange() {
  minIntensity.value = 1;
  maxIntensity.value = 5;
  emit("update-intensity", minIntensity.value, maxIntensity.value);
}

function restoreParameters() {
  supportedWordlist.value = false;
  requiredWordlist.value = false;
  emit("update-wordlist", supportedWordlist.value, requiredWordlist.value);
  requiredInputTechnology.value = false;
  emit("update-input-technology", requiredInputTechnology.value);
  requiredInputVulnerability.value = false;
  emit("update-input-vulnerability", requiredInputVulnerability.value);
}

function processConfiguration(configuration) {
  supportedWordlist.value = configuration.wordlists.supported;
  requiredWordlist.value =
    configuration.wordlists.supported && configuration.wordlists.required;
  emit("update-wordlist", supportedWordlist.value, requiredWordlist.value);
  requiredInputTechnology.value =
    configuration.input_technologies.supported &&
    configuration.input_technologies.required;
  emit("update-input-technology", requiredInputTechnology.value);
  requiredInputVulnerability.value =
    configuration.input_vulnerabilities.supported &&
    configuration.input_vulnerabilities.required;
  emit("update-input-vulnerability", requiredInputVulnerability.value);
}

function onTool(toolId) {
  tool.value = toolId;
  emit("update-tool", tool.value);
  restoreParameters();
  restoreIntensityRange();
  if (tool.value) {
    process.value = undefined;
    emit("update-process", process.value);
    configuration.value = undefined;
    emit("update-configuration", configuration.value);
    configurationOptions.value = [];
    props.api.get(`tools/${tool.value}/`).then((response) => {
      minIntensity.value = backend.intensities.find(
        (option) => option.label === response.intensities[0].value,
      )?.value;
      maxIntensity.value = backend.intensities.find(
        (option) =>
          option.label ===
          response.intensities[response.intensities.length - 1].value,
      )?.value;
      emit("update-intensity", minIntensity.value, maxIntensity.value);
      if (response.icon) {
        toolingAvatar.value = { src: response.icon };
        toolingIcon.value = undefined;
      } else {
        toolingAvatar.value = undefined;
        toolingIcon.value = "i-lucide-square-terminal";
      }
    });
    props.api
      .list("configurations/", { tool: tool.value }, true)
      .then((response) => {
        configurationOptions.value = response.items;
        defaultConfigurationObject.value = response.items.find(
          (configuration) => configuration.default,
        );
        configuration.value = defaultConfigurationObject.value.id;
        emit("update-configuration", configuration.value);
        processConfiguration(defaultConfigurationObject.value);
      });
  }
}

function onConfiguration(configurationId) {
  configuration.value = configurationId;
  emit("update-configuration", configuration.value);
  if (configuration.value) {
    props.api.get(`configurations/${configuration.value}/`).then((response) => {
      processConfiguration(response);
    });
  } else {
    restoreParameters();
  }
}

function onProcess(processId) {
  process.value = processId;
  emit("update-process", process.value);
  restoreParameters();
  restoreIntensityRange();
  if (process.value) {
    tool.value = undefined;
    emit("update-tool", tool.value);
    configuration.value = undefined;
    emit("update-configuration", configuration.value);
    configurationOptions.value = [];
    toolingAvatar.value = undefined;
    toolingIcon.value = "i-lucide-workflow";
    props.api.get(`processes/${process.value}/`).then((response) => {
      if (response.wordlists.supported) {
        supportedWordlist.value = true;
        requiredWordlist.value = response.wordlists.required;
        emit(
          "update-wordlist",
          supportedWordlist.value,
          requiredWordlist.value,
        );
      }
    });
  }
}

onMounted(() => {
  if (props.defaultConfiguration) {
    onConfiguration(props.defaultConfiguration);
  } else if (props.defaultTool) {
    onTool(props.defaultTool);
  } else if (props.defaultProcess) {
    onProcess(props.defaultProcess);
  } else {
    loadTooling();
  }
});
</script>
