<template>
  <UButton
    v-if="!onlyModal"
    icon="i-lucide-file-text"
    color="info"
    variant="subtle"
    aria-label="Generate report"
    @click="openModal = !openModal"
  />
  <LazyCrudFormModal
    :open="open ?? openModal"
    :api="api"
    :config="config"
    :item="
      taskId ? { task: taskId } : targetId ? { target: targetId } : undefined
    "
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
defineProps<{
  targetId?: number;
  taskId?: number;
  open?: boolean;
  onlyModal?: boolean;
}>();
const emit = defineEmits<{
  "update:open": [value: boolean];
}>();

const api = useApi("/api/reports/");
const route = useRoute();
const config = ref({
  entityName: "Report",
  editForm: resolveComponent("ReportsForm"),
  onCreation: () => navigateTo(`/projects/${route.params.project_id}/reports`),
});
const openModal = ref(false);

function handleOpen(open: boolean) {
  openModal.value = open;
  emit("update:open", open);
}
</script>
