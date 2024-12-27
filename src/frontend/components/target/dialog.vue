<template>
  <BaseDialog
    title="New Target"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <TargetForm
      v-if="parameters"
      :api="api"
      :project-id="parameters.project"
      @completed="$emit('completed')"
      @loading="(value) => (loading = value)"
    />
  </BaseDialog>
</template>

<script setup lang="ts">
defineProps({ api: Object, parameters: Object });
defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
</script>
