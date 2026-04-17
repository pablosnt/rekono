<template>
  <div>
    <UDropdownMenu
      v-if="userStore.is_auditor || finding.notes.length > 0"
      :items="
        [
          finding.notes.length > 0
            ? {
                label: `${finding.notes.length} Notes`,
                icon: 'i-lucide-notebook',
                color: 'neutral',
                to: `/projects/${finding.project}/notes?${entityName.toLowerCase()}=${finding.id}`,
              }
            : {},
          userStore.is_auditor
            ? {
                label: 'Take note',
                icon: 'i-lucide-plus',
                color: 'neutral',
                onSelect: () => nextTick(() => notesButton?.createNote()),
              }
            : {},
        ].filter((i) => Object.keys(i).length > 0)
      "
      :content="{ align: 'end' }"
    >
      <UButton icon="i-lucide-notebook" variant="ghost" color="neutral" />
    </UDropdownMenu>
    <NotesButton
      v-if="userStore.is_auditor"
      ref="notesButton"
      :show="false"
      v-bind="noteProps"
    />
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import type { Finding } from "~/types/models";

const props = defineProps<{ finding: Finding; entityName: string }>();

const userStore = useUserStore();
const notesButton = ref();
const noteProps = computed(() => {
  return {
    [props.entityName.toLowerCase()]: props.finding.id,
    project: props.finding.project,
  };
});
</script>
