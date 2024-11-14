<template>
  <v-card :title="process.name" elevation="3" density="compact" hover>
    <template #append>
      <UtilsCounterChip
        :collection="process.steps"
        entity="Steps"
        icon="mdi-rocket"
      />
      <span class="me-3" />
      <UtilsOwner :entity="process" />
      <BaseButton
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
          <BaseTagShow :tags="process.tags" divider />
        </div>
        <div v-if="details">
          <ProcessFormSteps
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
      <UtilsLike
        :api="api"
        :item="process"
        @reload="(value) => $emit('reload', value)"
      />
      <UtilsDeleteButtonEdit
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
      </UtilsDeleteButtonEdit>
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
