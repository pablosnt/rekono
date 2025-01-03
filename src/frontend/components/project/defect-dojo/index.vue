<template>
  <ProjectDefectDojoButton
    v-if="
      (onlyLink || !autz.isAuditor()) &&
      settings !== null &&
      settings.server !== null &&
      project.defectdojo_sync !== null &&
      (project.defectdojo_sync.product_id !== null ||
        project.defectdojo_sync.engagement_id !== null)
    "
    :project="project"
    :settings="settings"
    :integration="integration"
    size="x-large"
    :avatar-size="avatarSize"
    link
  />

  <v-speed-dial
    v-if="
      !onlyLink &&
      autz.isAuditor() &&
      settings !== null &&
      settings.server !== null &&
      settings.is_available &&
      integration !== null &&
      integration.enabled &&
      project.defectdojo_sync !== null
    "
    transition="scale-transition"
    location="bottom center"
    open-on-hover
  >
    <template #activator="{ props: activatorProps }">
      <ProjectDefectDojoButton
        v-bind="activatorProps"
        :project="project"
        :settings="settings"
        :integration="integration"
        size="x-large"
        :avatar-size="avatarSize"
      />
    </template>
    <ProjectDefectDojoButton
      v-if="
        project.defectdojo_sync.product_id !== null ||
        project.defectdojo_sync.engagement_id !== null
      "
      :project="project"
      :settings="settings"
      :integration="integration"
      variant="elevated"
      icon="mdi-link"
      color
      link
    />
    <v-dialog width="500" class="overflow-auto">
      <template #activator="{ props: activatorProps }">
        <BaseButton variant="flat" color="red" icon="mdi-link-off" v-bind="activatorProps" />
      </template>
      <template #default="{ isActive }">
        <UtilsDeleteDialog
          :id="project.defectdojo_sync.id"
          :api="api"
          text="Defect-Dojo synchronization will be disabled"
          action="Disable"
          @completed="
            isActive.value = false;
            $emit('reload');
          "
          @close-dialog="isActive.value = false"
        />
      </template>
    </v-dialog>
  </v-speed-dial>

  <v-dialog
    v-if="
      !onlyLink &&
      autz.isAuditor() &&
      settings !== null &&
      settings.is_available &&
      integration !== null &&
      integration.enabled &&
      project.defectdojo_sync === null
    "
    width="auto"
  >
    <template #activator="{ props: activatorProps }">
      <ProjectDefectDojoButton
        v-bind="activatorProps"
        :project="project"
        :settings="settings"
        :integration="integration"
        size="x-large"
        :avatar-size="avatarSize"
      />
    </template>
    <template #default="{ isActive }">
      <ProjectDefectDojoDialog
        :api="api"
        :project="project"
        :integration="integration"
        @close-dialog="isActive.value = false"
        @completed="
          isActive.value = false;
          $emit('reload');
        "
      />
    </template>
  </v-dialog>
</template>

<script setup lang="ts">
defineProps({
  project: Object,
  onlyLink: { type: Boolean, required: false, default: false },
  avatarSize: {type: String, required: false, default: 'small'}
});
defineEmits(["reload"]);
const autz = useAutz()
const integration = ref({ enabled: false });
const settings = ref({ is_available: false });
const api = useApi("/api/defect-dojo/sync/", true, "Defect-Dojo sync");
useApi("/api/integrations/", true)
  .get(1)
  .then((integrationResponse) => {
    integration.value = integrationResponse;
  });
useApi("/api/defect-dojo/settings/", true)
  .get(1)
  .then((settingsResponse) => {
    settings.value = settingsResponse;
  });
</script>
