<template>
  <DialogDefault
    title="New Project"
    :loading="loading"
    @close-dialog="
      loading = false;
      project !== null ? navigateTo(`/projects/${project.id}`) : $emit('closeDialog');;
    "
  >
    <v-stepper v-model="step" hide-actions>
      <v-stepper-header>
        <v-stepper-item title="Project" icon="mdi-folder-open" color="red" />
        <v-stepper-item title="Targets" icon="mdi-target" color="red" />
      </v-stepper-header>
      <v-stepper-window>
        <FormProcessProject
          v-if="step === 0"
          :api="api"
          @completed="
            (response) => {
              project = response;
              step = 1;
            }
              "
          @loading="(value) => (loading = value)"
        />
        <FormTarget
          v-if="step === 1"
          :project="project"
          @completed="navigateTo(`/projects/${project.id}`)"
          @loading="(value) => (loading = value)"
        />
      </v-stepper-window>
    </v-stepper>
  </DialogDefault>
</template>

<script setup lang="ts">
defineProps({ api: Object });
const emit = defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
const step = ref(0);
const project = ref(null);
</script>
