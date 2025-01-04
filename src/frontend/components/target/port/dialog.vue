<template>
  <BaseDialog
    title="New Scope"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
      targetPort !== null ? $emit('completed') : null;
    "
  >
    <v-stepper v-model="step" hide-actions flat>
      <v-stepper-header>
        <v-stepper-item
          title="Target Port"
          :icon="enums.findings.Port.icon"
          color="red"
        />
        <v-stepper-item
          title="Authentication"
          icon="mdi-shield-account"
          color="red"
        />
      </v-stepper-header>
      <v-stepper-window>
        <TargetPortForm
          v-if="step === 0"
          :api="api"
          @completed="
            (response) => {
              targetPort = response;
              step = 1;
            }
          "
          @loading="(value) => (loading = value)"
        />
        <TargetPortAuthenticationForm
          v-if="step === 1"
          :target-port="targetPort.id"
          @completed="$emit('completed')"
          @loading="(value) => (loading = value)"
        />
      </v-stepper-window>
    </v-stepper>
  </BaseDialog>
</template>

<script setup lang="ts">
defineProps({ api: Object });
defineEmits(["closeDialog", "completed"]);
const enums = useEnums();
const loading = ref(false);
const step = ref(0);
const targetPort = ref(null);
</script>
