<template>
  <DialogDefault
    title="Delete Confirmation"
    :loading="false"
    color="red"
    width="400"
    @close-dialog="$emit('closeDialog')"
  >
    <template #default>
      <p>{{ text }}</p>
      <p><strong>Are you sure?</strong></p>
    </template>
    <template #card>
      <v-card-actions>
        <v-btn
          prepend-icon="mdi-close"
          color="blue-grey"
          @click="$emit('closeDialog')"
          >Cancel</v-btn
        >
        <v-spacer />
        <v-btn
          prepend-icon="mdi-trash-can-outline"
          color="grey-lighten-5"
          @click="
            api.remove(id).then(() => {
              $emit('completed');
            })
          "
          >Delete</v-btn
        >
      </v-card-actions>
    </template>
  </DialogDefault>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  id: Number,
  text: String,
});
</script>
