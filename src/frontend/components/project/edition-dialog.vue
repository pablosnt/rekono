<template>
  <Dialog
    title="Edit Project"
    :loading="loading"
    @close-dialog="emit('closeDialog')"
  >
    <ProcessProjectForm
      :api="api"
      :edit="edit"
      @loading="(value) => (loading = value)"
      @completed="
        () => {
          loading = false;
          emit('completed');
        }
      "
    />
  </Dialog>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  edit: Object,
});
const emit = defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
</script>
