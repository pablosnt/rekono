<template>
  <DialogDefault
    title="Edit Project"
    :loading="loading"
    @close-dialog="emit('closeDialog')"
  >
    <FormProcessProject
      :api="api"
      :edit="edit"
      @loading="(value) => (loading = value)"
      @completed="
        () => {
          emit('completed');
          loading = false;
          emit('closeDialog');
        }
      "
    />
  </DialogDefault>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  edit: Object,
});
const emit = defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
</script>
