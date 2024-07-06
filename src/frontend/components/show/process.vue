<template>
  <v-card :title="process.name" elevation="3" density="compact" hover>
    <template #append>
      <v-chip v-if="process.steps" color="red">
        <v-icon icon="mdi-rocket" start />3 {{ process.steps.length }} Steps
      </v-chip>
      <span class="me-3" />
      <v-chip
        v-if="process.owner"
        color="primary"
        :variant="process.owner.id === user.user ? 'flat' : 'tonal'"
      >
        <v-icon icon="mdi-at" start />
        {{ process.owner.username }}
      </v-chip>
      <v-chip v-if="!process.owner">Default</v-chip>
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
          <div v-if="process.tags.length > 0">
            <v-divider class="mt-3 mb-3" />
            <v-chip-group selected-class="v-chip">
              <v-chip v-for="tag in process.tags" :key="tag" size="small">
                {{ tag }}
              </v-chip>
            </v-chip-group>
          </div>
        </div>
        <div v-if="details">
          <FormSteps
            :process="process"
            :tools="tools"
            @reload="() => $emit('reload', false)"
          />
        </div>
      </v-card-text>

      <v-card-actions>
        <ButtonRun :process="process" />
        <v-spacer />
        <ButtonLike
          :api="api"
          :item="process"
          @reload="(value) => $emit('reload', value)"
        />
        <ButtonEditDelete
          v-if="
            (process.owner !== null && process.owner.id === user.user) ||
            user.role === 'Admin'
          "
        >
          <template #edit-dialog="{ isActive }">
            <DialogProcess
              :api="api"
              :edit="process"
              :tools="tools"
              @completed="$emit('reload', false)"
              @close-dialog="isActive.value = false"
            />
          </template>
          <template #delete-dialog="{ isActive }">
            <DialogDelete
              :id="process.id"
              :api="api"
              :text="`Process '${process.name}' will be removed`"
              @completed="$emit('reload', false)"
              @close-dialog="isActive.value = false"
            />
          </template>
        </ButtonEditDelete>
      </v-card-actions>
    </template>
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
