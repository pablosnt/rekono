<template>
  <BaseDialog
    :title="edit ? 'Edit Process' : step === 1 ? process.name : 'New process'"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit(step === 1 ? 'completed' : 'closeDialog');
    "
  >
    <ProcessFormProject
      v-if="step === 0"
      :api="api"
      :edit="edit ? edit : process"
      @loading="(value) => (loading = value)"
      @completed="
        (data) => {
          loading = false;
          edit
            ? $emit('completed')
            : ((process = data), (loading = false), (step = 1));
        }
      "
    />
    <ProcessFormSteps v-if="step === 1" :process="process" />
  </BaseDialog>
</template>

<script setup lang="ts">
defineProps({ api: Object, edit: Object });
defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
const process = ref(null);
const step = ref(0);
</script>
