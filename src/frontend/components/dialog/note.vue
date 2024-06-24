<template>
  <DialogDefault
    :title="undefined"
    :loading="false"
    @close-dialog="$emit('closeDialog')"
  >
    <FormNote />
  </DialogDefault>
</template>

<script setup lang="ts">
defineEmits(["closeDialog"]);
</script>
