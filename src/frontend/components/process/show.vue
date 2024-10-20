<template>
  <v-card :title="process.name" elevation="3" density="compact" hover>
    <template #append>
      <UtilsCounter
        :collection="process.steps"
        entity="Steps"
        icon="mdi-rocket"
      />
      <span class="me-3" />
      <UtilsOwner :entity="process" />
      <v-btn
        v-if="details"
        icon="mdi-close"
        variant="text"
        @click="$emit('closeDialog')"
      />
    </template>
    <template #text>
      <v-card-text class="overflow-auto">
        <div v-if="!details">
          <p>{{ process.description }}</p>
          <TagShow :item="process" divider />
        </div>
        <div v-if="details">
          <ProcessStepsForm
            :process="process"
            :tools="tools"
            @reload="() => $emit('reload', false)"
          />
        </div>
      </v-card-text>
    </template>
    <v-card-actions>
      <TaskButton :process="process" tooltip="Run" />
      <v-spacer />
      <UtilsButtonLike
        :api="api"
        :item="process"
        @reload="(value) => $emit('reload', value)"
      />
      <UtilsButtonEditDelete
        v-if="
          (process.owner !== null && process.owner.id === user.user) ||
          user.role === 'Admin'
        "
      >
        <template #edit-dialog="{ isActive }">
          <ProcessDialog
            :api="api"
            :edit="process"
            :tools="tools"
            @completed="$emit('reload', false)"
            @close-dialog="isActive.value = false"
          />
        </template>
        <template #delete-dialog="{ isActive }">
          <UtilsDeleteDialog
            :id="process.id"
            :api="api"
            :text="`Process '${process.name}' will be removed`"
            @completed="$emit('reload', false)"
            @close-dialog="isActive.value = false"
          />
        </template>
      </UtilsButtonEditDelete>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  process: Object,
  tools: Array,
  details: Boolean,
});
defineEmits(["reload", "closeDialog"]);
const user = userStore();
</script>
