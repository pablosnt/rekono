<template>
  <div>
    <template v-if="relatedEntity.notes.length > 0">
      <UDropdownMenu
        :items="[
          {
            label: `${relatedEntity.notes.length} Notes`,
            icon: 'i-lucide-notebook',
            color: 'neutral',
            to: `/projects/${project}/notes?${entityNameLower}=${relatedEntity.id}`,
          },
          {
            label: 'Take note',
            icon: 'i-lucide-plus',
            color: 'neutral',
            onSelect: () => nextTick(() => notesButton?.createNote()),
          },
        ]"
        :content="{ align: 'end' }"
      >
        <UChip
          :text="formatCount(relatedEntity.notes.length)"
          size="3xl"
          color="neutral"
          position="top-right"
        >
          <UButton
            icon="i-lucide-notebook"
            :variant="variant"
            color="neutral"
            aria-label="Related notes"
          />
        </UChip>
      </UDropdownMenu>
    </template>
    <NotesButton
      ref="notesButton"
      :show="relatedEntity.notes.length === 0"
      v-bind="noteProps"
      icon="i-lucide-notebook"
      color="neutral"
      :variant="variant"
    />
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    relatedEntity: object;
    entityName: string;
    project: number;
    variant?: string;
  }>(),
  { variant: "ghost" },
);

const notesButton = ref();
const entityNameLower = props.entityName.toLowerCase();
const noteProps = computed(() => {
  return {
    [entityNameLower]: props.relatedEntity.id,
    project: props.project,
  };
});
</script>
