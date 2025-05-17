<template>
  <v-card
    :title="process.name"
    :subtitle="`${utils.displayNumber(process.steps.length)} steps`"
    elevation="2"
    :class="details ? '' : 'ma-3'"
    density="comfortable"
    :hover="!details"
  >
    <template #append>
      <TaskButton
        v-if="details"
        :process="process"
        tooltip="Run"
        :disabled="process.steps.length === 0"
      />
      <UtilsLike
        class="mr-6"
        :api="api"
        :item="process"
        @reload="(value) => $emit('reload', value)"
      />
      <UtilsOwner class="mr-2" :entity="process" />
      <ProcessEditDelete
        v-if="details"
        :api="api"
        :process="process"
        :tools="tools"
        @reload="$emit('reload', false)"
      />
      <BaseButton
        v-if="details"
        icon="mdi-close"
        variant="text"
        @click="$emit('closeDialog')"
      />
    </template>
    <template #text>
      <template v-if="!details">
        <p class="text-center">{{ process.description }}</p>
        <BaseTagShow :tags="process.tags" divider />
      </template>
      <div v-if="details">
        <ProcessFormSteps :process="process" />
      </div>
    </template>
    <v-card-actions v-if="!details">
      <TaskButton
        :process="process"
        tooltip="Run"
        :disabled="process.steps.length === 0"
      />
      <v-spacer />
      <ProcessEditDelete
        :api="api"
        :process="process"
        :tools="tools"
        @reload="$emit('reload', false)"
      />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  process: Object,
  tools: Array,
  details: Boolean,
});
defineEmits(["reload", "closeDialog"]);
const utils = useUtils();
</script>
