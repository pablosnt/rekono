<template>
  <MenuProject>
    <v-container fluid>
      <v-card :title="project.name" variant="text">
        <template #prepend>
          <v-avatar
            v-if="project && project.name"
            class="mr-2"
            color="red-accent-4"
          >
            <span class="text-h5 text">{{
              project.name.charAt(0).toUpperCase()
            }}</span>
          </v-avatar>
        </template>
        <template #append>
          <TaskButton :project="project" />
          <ProjectDefectDojo :project="project" @reload="loadData()" />
          <UtilsDeleteButtonEdit
            v-if="
              project.owner &&
              (project.owner.id === user.user || user.role === 'Admin')
            "
          >
            <template #edit-dialog="{ isActive }">
              <ProjectDialogEdit
                :api="api"
                :edit="project"
                @completed="
                  loadData();
                  isActive.value = false;
                "
                @close-dialog="isActive.value = false"
              />
            </template>
            <template #delete-dialog="{ isActive }">
              <UtilsDeleteDialog
                :id="project.id"
                :api="api"
                :text="`Project '${project.name}' will be removed`"
                @completed="
                  navigateTo('/projects');
                  isActive.value = false;
                "
                @close-dialog="isActive.value = false"
              />
            </template>
          </UtilsDeleteButtonEdit>
        </template>
        <template #text>
          <p class="text-center">{{ project.description }}</p>
          <BaseTagShow :tags="project.tags" divider />
          <Dashboard />
        </template>
      </v-card>
    </v-container>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const user = userStore();
const route = useRoute();
const api = useApi("/api/projects/", true);
const project = ref({
  id: route.params.project_id,
  name: undefined,
  description: "",
  tags: [],
});
loadData();

function loadData(): void {
  api
    .get(route.params.project_id)
    .then((response) => (project.value = response));
}
</script>
