<template>
  <v-dialog width="500" class="overflow-auto">
    <template #activator="{ props: activatorProps }">
      <BaseButton
        hover
        :variant="variant"
        :icon="icon"
        icon-color="red"
        :tooltip="action"
        v-bind="activatorProps"
      />
    </template>
    <template #default="{ isActive }">
      <UtilsDeleteDialog
        :id="id"
        :api="api"
        :text="text"
        :action="action"
        @completed="
          $emit('completed');
          isActive.value = false;
        "
        @close-dialog="isActive.value = false"
      />
    </template>
  </v-dialog>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  id: Number,
  text: String,
  action: {
    type: String,
    required: false,
    default: "Delete",
  },
  icon: {
    type: String,
    required: false,
    default: "mdi-close",
  },
  variant: {
    type: String,
    required: false,
    default: "text",
  },
});
defineEmits(["completed"]);
</script>
