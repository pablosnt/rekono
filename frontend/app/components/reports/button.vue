<template>
  <UButton
    v-if="show !== false"
    icon="i-lucide-file-text"
    color="info"
    variant="subtle"
    @click="openModal = !openModal"
  />
  <CrudFormModal
    :open="open ?? openModal"
    :api="api"
    :config="config"
    :item="taskId ? {task: taskId} : targetId ? {target: targetId} : undefined"
    title="Generate Report"
    submit-label="Generate"
    :ui="{
      content: 'sm:max-w-4xl sm:max-h-xl',
      footer: 'justify-end',
    }"
    @open="handleOpen"
  />
</template>

<script setup lang="ts">
const props = defineProps<{
  targetId?: number;
  taskId?: number;
  open?: boolean;
  show?: boolean;
}>();

const emit = defineEmits<{
  'update:open': [value: boolean];
}>();

const api = useApi("/api/reports/");
const route = useRoute()
const config = ref({
  entityName: "Report",
  editForm: resolveComponent("ReportsForm"),
  onCreation: (data: Record<string, unknown>) =>
    navigateTo(`/projects/${route.params.project_id}/reports`),
});
const openModal = ref(false);

function handleOpen(open: boolean) {
  openModal.value = open;
  emit('update:open', open);
}
</script>