<template>
  <div v-if="userStore.is_auditor || relatedEntity.notes.length > 0">
    <template v-if="relatedEntity.notes.length > 0">
      <UDropdownMenu
        :items="[
          {
            label: `${relatedEntity.notes.length} Notes`,
            icon: 'i-lucide-notebook',
            color: 'neutral',
            to: `/projects/${project}/notes?${entityName.toLowerCase()}=${relatedEntity.id}`,
          },
          ...(userStore.is_auditor
            ? [
                {
                  label: 'Take note',
                  icon: 'i-lucide-plus',
                  color: 'neutral',
                  onSelect: () => nextTick(() => notesButton?.createNote()),
                },
              ]
            : []),
        ]"
        :content="{ align: 'end' }"
      >
        <UChip
          :text="relatedEntity.notes.length.toString()"
          size="3xl"
          color="neutral"
          position="top-right"
        >
          <UButton icon="i-lucide-notebook" variant="ghost" color="neutral" />
        </UChip>
      </UDropdownMenu>
    </template>
    <NotesButton
      v-if="userStore.is_auditor"
      ref="notesButton"
      :show="relatedEntity.notes.length === 0"
      v-bind="noteProps"
      icon="i-lucide-notebook"
      color="neutral"
      variant="ghost"
    />
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const props = defineProps<{
  relatedEntity: object;
  entityName: string;
  project: number;
}>();

const userStore = useUserStore();
const notesButton = ref();
const noteProps = computed(() => {
  return {
    [props.entityName.toLowerCase()]: props.relatedEntity.id,
    project: props.project,
  };
});
</script>
