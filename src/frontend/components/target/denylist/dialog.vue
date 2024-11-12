<template>
  <BaseDialog
    title="New Target Pattern To Deny"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
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
