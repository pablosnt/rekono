<template>
  <v-dialog width="500" class="overflow-auto">
    <template #activator="{ props: activatorProps }">
      <BaseButton
        hover
        :variant="variant"
        :color="color"
        :icon="icon"
        :icon-color="iconColor"
        :tooltip="action"
        :size="size"
        v-bind="activatorProps"
      />
    </template>
    <template #default="{ isActive }">
      <UtilsDeleteDialog
        :id="id"
        :api="api"
        :text="text"
        :icon="iconConfirmation"
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
  iconConfirmation: {
    type: String,
    required: false,
    default: "mdi-trash-can-outline",
  },
  variant: {
    type: String,
    required: false,
    default: "text",
  },
  iconColor: {
    type: String,
    required: false,
    default: "red",
  },
  color: {
    type: String,
    required: false,
    default: undefined,
  },
  size: {
    type: String,
    required: false,
    default: undefined,
  },
});
defineEmits(["completed"]);
</script>
