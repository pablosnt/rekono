<template>
  <DialogDefault
    title="New HTTP Header"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('closeDialog');
    "
  >
    <template #default>
      <FormHttpHeader
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
    </template>
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
