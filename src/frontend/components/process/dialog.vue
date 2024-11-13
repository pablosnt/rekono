<template>
  <BaseDialog
    :title="edit ? 'Edit Process' : step === 1 ? process.name : 'New process'"
    :loading="loading"
    @close-dialog="closeDialog(step === 1)"
  >
    <ProcessFormProject
      v-if="step === 0"
      :api="api"
      :edit="edit ? edit : process"
      @loading="(value) => (loading = value)"
      @completed="
        (data) => {
          edit ? closeDialog(true) : createdProcess(data);
        }
      "
    />
    <ProcessFormSteps
      v-if="step === 1"
      :process="process"
      @reload="api.get(process.id).then((response) => (process = response))"
    />
  </BaseDialog>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  edit: Object,
});
const emit = defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
const process = ref(null);
const step = ref(0);
function createdProcess(data: object): void {
  process.value = data;
  loading.value = false;
  step.value = 1;
}
function closeDialog(completed: boolean): void {
  if (completed) {
    emit("completed");
  }
  loading.value = false;
  emit("closeDialog");
}
</script>
