<template>
  <UModal
    :open="open"
    :title="`${config.deleteVerb || 'Delete'} ${config.entityName}`"
    :ui="{ content: 'sm:max-w-3xl sm:max-h-xl', footer: 'justify-end' }"
    :loading="loading"
    @update:open="(val) => $emit('open', val)"
  >
    <template #body>
      <template v-if="item">
        <template
          v-for="(message, index) in config.deleteMessage?.(item) || [
            {
              component: h(
                'p',
                { class: 'text-gray-900 dark:text-white font-medium' },
                `Are you sure you want to delete this ${config.entityName.toLowerCase()}? This action can't be undone.`,
              ),
            },
          ]"
          :key="index"
        >
          <component :is="message.component" v-bind="message.props || {}" />
        </template>
      </template>
    </template>
    <template #footer="{ close }">
      <UButton
        label="Cancel"
        color="neutral"
        variant="outline"
        @click="close"
      />
      <UButton
        color="primary"
        :label="config.deleteVerb || 'Delete'"
        :loading="loading"
        @click="remove"
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";

const props = defineProps<{
  open: boolean;
  item: Record<string, string | number | boolean | null>;
  config: CrudConfig;
  api: object;
}>();

const emit = defineEmits<{
  open: [open: boolean];
  deleted: [];
}>();

const loading = ref(false);

function remove() {
  loading.value = true;
  props.api
    .remove(`${props.item.id}/`, {}, props.config.entityName)
    .then(() => {
      emit("deleted");
      emit("open", false);
    })
    .finally(() => {
      loading.value = false;
    });
}
</script>
