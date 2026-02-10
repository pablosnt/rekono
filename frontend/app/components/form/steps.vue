<template>
  <USelectMenu
    v-model="toolFilter"
    placeholder="Filter by tool"
    size="xl"
    class="w-full mb-4"
    :items="
      tools.map((tool) => {
        return {
          avatar: tool.icon ? { src: tool.icon } : undefined,
          icon: tool.icon ? undefined : 'i-lucide-square-terminal',
          label: tool.name,
          value: tool.id,
        };
      })
    "
    value-key="value"
    label-key="label"
    :icon="toolFilter ? undefined : 'i-lucide-square-terminal'"
    :avatar="
      toolFilter
        ? { src: tools.find((tool) => tool.id === toolFilter)?.icon }
        : undefined
    "
    leading
    @update:model-value="(value) => fetch()"
  >
    <template #trailing>
      <UIcon
        v-if="toolFilter === null || toolFilter === undefined"
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
          toolFilter = undefined;
          fetch();
        "
      />
    </template>
  </USelectMenu>
  <UAccordion
    :model-value="utils.stageOptions.map((stage) => stage.value)"
    :items="
      utils.stageOptions.filter(
        (stage) =>
          tools.filter(
            (tool) =>
              getToolConfigurationsPerStage(tool, stage.label).length > 0,
          ).length > 0,
      )
    "
    type="multiple"
  >
    <template #default="{ item: stage }">
      <p class="text-xl">{{ stage.label }}</p>
    </template>
    <template #body="{ item: stageBody }">
      <UTree
        color="neutral"
        size="xl"
        :items="getStageTree(stageBody.label)"
        multiple
        selection-behavior="replace"
      >
        <template #item-leading="{ item: toolNode }">
          <template v-if="Object.hasOwn(toolNode, 'avatar')">
            <UAvatar v-if="toolNode.avatar" :src="toolNode.avatar" />
            <UIcon
              v-else
              name="i-lucide-square-terminal"
              class="text-xl text-primary"
            />
          </template>
        </template>
        <template #item-trailing="{ item: configNode }">
          <USwitch
            v-if="Object.hasOwn(configNode, 'id')"
            :model-value="configurations.includes(configNode.id)"
            @update:model-value="
              (value) =>
                value ? addStep(configNode.id) : removeStep(configNode.id)
            "
          />
        </template>
      </UTree>
    </template>
  </UAccordion>
</template>

<script setup lang="ts">
import type { Configuration, Tool, Process } from "~/types/models";

const props = defineProps<{ process: Process }>();
const emit = defineEmits<{
  "new-loading": [newLoading: boolean];
}>();

const utils = useUtils();
const api = useApi("/api/");
const tools = ref<Array<Tool>>([]);
const configurations = ref(
  props.process.steps.map((step) => step.configuration.id),
);
const toolFilter = ref();

function getToolConfigurationsPerStage(
  tool: Tool,
  stage: string,
): Configuration[] {
  return tool.configurations.filter(
    (configuration) =>
      configuration.stage === stage && !configuration.deprecated,
  );
}

function getStageTree(stage: string): Array {
  const tree = [];
  tools.value.forEach((tool) => {
    const configurationsPerStage = getToolConfigurationsPerStage(tool, stage);
    if (configurationsPerStage.length > 0) {
      tree.push({
        label: tool.name,
        avatar: tool.icon,
        defaultExpanded:
          configurationsPerStage.filter((configuration) =>
            configurations.value.includes(configuration.id),
          ).length > 0,
        children: configurationsPerStage.map((configuration) => {
          return {
            label: configuration.name,
            id: configuration.id,
            default: configuration.default,
          };
        }),
      });
    }
  });
  return tree;
}

function addStep(configuration: number) {
  emit("new-loading", true);
  api
    .create(
      "steps/",
      {
        process_id: props.process.id,
        configuration_id: configuration,
      },
      {},
      "Step",
    )
    .then(() => configurations.value.push(configuration))
    .finally(() => emit("new-loading", false));
}

function removeStep(configuration: number) {
  emit("new-loading", true);
  api
    .list(
      "steps/",
      { configuration: configuration, process: props.process.id },
      false,
      1,
      1,
    )
    .then((response) => {
      if (response.total === 1) {
        api
          .remove(`steps/${response.items[0].id}/`, {}, "Step")
          .then(() =>
            configurations.value.splice(
              configurations.value.indexOf(configuration),
              1,
            ),
          );
      }
    })
    .finally(() => emit("new-loading", false));
}

function fetch() {
  if (toolFilter.value) {
    api
      .get(`tools/${toolFilter.value}/`)
      .then((response) => (tools.value = [response]));
  } else {
    api
      .list("tools/", {}, true)
      .then((response) => (tools.value = response.items));
  }
}

onMounted(() => {
  fetch();
});
</script>
