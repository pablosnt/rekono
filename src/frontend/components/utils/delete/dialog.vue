<template>
  <BaseDialog
    :title="`${action} Confirmation`"
    :loading="false"
    color="red"
    width="400"
    @close-dialog="$emit('closeDialog')"
  >
    <template #default>
      <p>{{ text }}</p>
      <p><strong>Are you sure?</strong></p>
    </template>
    <template #actions>
      <v-card-actions>
        <v-btn
          prepend-icon="mdi-close"
          color="blue-grey"
          @click="$emit('closeDialog')"
          >{{ action !== "Cancel" ? "Cancel" : "Abort" }}</v-btn
        >
        <v-spacer />
        <v-btn
          :prepend-icon="icon"
          color="grey-lighten-5"
          @click="
            api.remove(id).then(() => {
              $emit('completed');
            })
          "
          >{{ action }}</v-btn
        >
      </v-card-actions>
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  id: Number,
  text: String,
  icon: { type: String, required: false, default: "mdi-trash-can-outline" },
  action: { type: String, required: false, default: "Delete" },
});
defineEmits(["closeDialog", "completed"]);
</script>
