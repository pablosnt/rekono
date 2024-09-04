<template>
  <v-dialog width="500" class="overflow-auto">
    <template #activator="{ props: activatorProps }">
      <v-btn hover variant="text" icon v-bind="activatorProps">
        <v-icon :icon="icon" color="red" />
        <v-tooltip activator="parent" text="Delete" />
      </v-btn>
    </template>
    <template #default="{ isActive }">
      <UtilsDeleteDialog
        :id="id"
        :api="api"
        :text="text"
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
  icon: {
    type: String,
    required: false,
    default: "mdi-close",
  },
});
defineEmits(["completed"]);
</script>
