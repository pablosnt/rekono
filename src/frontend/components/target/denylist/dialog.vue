<template>
  <BaseDialog
    title="New Denied Target"
    :loading="loading"
    @close-dialog="$emit('closeDialog')"
  >
    <TargetDenylistForm
      :api="api"
      @loading="(value) => (loading = value)"
      @completed="
        () => {
          loading = false;
          $emit('completed');
        }
      "
    />
  </BaseDialog>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  edit: Object,
});
defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
</script>
