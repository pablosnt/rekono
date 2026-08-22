<template>
  <div>
    <template v-if="relatedEntity.reports.length > 0">
      <UDropdownMenu
        :items="[
          {
            label: pluralize(relatedEntity.reports.length, 'Report'),
            icon: 'i-lucide-file-text',
            to: `/projects/${project}/reports${entityNameLowerCase && entityNameLowerCase !== 'project' ? `?${entityNameLowerCase}=${relatedEntity?.id}` : ''}`,
          },
          {
            label: 'Generate a report',
            icon: 'i-lucide-plus',
            onSelect: () => (reportModalOpen = true),
          },
        ]"
        :content="{ align: 'end' }"
      >
        <UChip
          :text="formatCount(relatedEntity.reports.length)"
          color="neutral"
          position="top-right"
          :ui="{ base: 'h-4 min-w-4 px-1 text-[10px] leading-none' }"
        >
          <UButton
            icon="i-lucide-file-text"
            :variant="variant"
            color="neutral"
            aria-label="Related reports"
          />
        </UChip>
      </UDropdownMenu>
      <ReportsButton
        v-model:open="reportModalOpen"
        :target-id="targetId"
        :task-id="taskId"
        only-modal
      />
    </template>
    <ReportsButton
      v-else
      :target-id="targetId"
      :task-id="taskId"
      :color="color"
      :variant="variant"
    />
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    relatedEntity: { id: number; reports: unknown[]; target?: { id: number } };
    entityName: string;
    project: number;
    color?: string;
    variant?: string;
  }>(),
  { color: "info", variant: "ghost" },
);

const reportModalOpen = ref(false);
const entityNameLowerCase = props.entityName.toLowerCase();
const targetId =
  entityNameLowerCase === "target" ? props.relatedEntity.id : undefined;
const taskId =
  entityNameLowerCase === "task" ? props.relatedEntity.id : undefined;
</script>
