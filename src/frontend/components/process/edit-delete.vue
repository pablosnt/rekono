<template>
  <UtilsDeleteButtonEdit v-if="autz.isOwner(process) || autz.isAdmin()">
    <template #edit-dialog="{ isActive }">
      <ProcessDialog
        :api="api"
        :edit="process"
        :tools="tools"
        @completed="
          isActive.value = false;
          $emit('reload');
        "
        @close-dialog="isActive.value = false"
      />
    </template>
    <template #delete-dialog="{ isActive }">
      <UtilsDeleteDialog
        :id="process.id"
        :api="api"
        :text="`Process '${process.name}' will be removed`"
        @completed="
          isActive.value = false;
          $emit('reload');
        "
        @close-dialog="isActive.value = false"
      />
    </template>
  </UtilsDeleteButtonEdit>
</template>

<script setup lang="ts">
defineProps({ api: Object, process: Object, tools: Array });
defineEmits(["reload"]);
const autz = useAutz();
</script>
