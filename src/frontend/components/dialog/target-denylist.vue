<template>
  <DialogDefault
    title="New Target Pattern To Deny"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <FormTargetDenylist
      :api="api"
      @loading="(value) => (loading = value)"
      @completed="
        () => {
          loading = false;
          $emit('closeDialog');
          $emit('completed');
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
defineEmits(["closeDialog", "completed"]);
const loading = ref(false);
</script>
