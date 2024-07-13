<template>
  <DialogDefault
    title="New Target"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <FormTarget
      v-if="parameters"
      :api="api"
      :project-id="parameters.project"
      @completed="
        () => {
          $emit('completed');
          $emit('closeDialog');
        }
      "
      @loading="(value) => (loading = value)"
    />
  </DialogDefault>
</template>

<script setup lang="ts">
defineProps({ api: Object, parameters: Object });
defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
</script>
