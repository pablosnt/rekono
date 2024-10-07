<template>
  <Dialog
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
  </Dialog>
</template>

<script setup lang="ts">
defineProps({ api: Object, targetPort: Number });
defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
</script>
