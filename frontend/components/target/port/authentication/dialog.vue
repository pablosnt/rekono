<template>
  <BaseDialog
    title="New Authentication"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <TargetPortAuthenticationForm
      :target-port="targetPort"
      @completed="$emit('completed')"
      @loading="(value) => (loading = value)"
    />
  </BaseDialog>
</template>

<script setup lang="ts">
defineProps({ api: Object, targetPort: Number });
defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
</script>
