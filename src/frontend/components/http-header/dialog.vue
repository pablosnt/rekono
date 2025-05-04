<template>
  <BaseDialog
    title="New HTTP Header"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <HttpHeaderForm
      :api="api"
      :parameters="parameters"
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
  parameters: { type: Object, required: false, default: null },
});
defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
</script>
