<template>
  <v-dialog width="500" class="overflow-auto">
    <template #activator="{ props: activatorProps }">
      <v-btn
        hover
        :variant="variant"
        icon
        v-bind="activatorProps"
        @click.prevent.stop
      >
        <v-icon :icon="icon" color="red" />
        <v-tooltip activator="parent" :text="action" />
      </v-btn>
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
