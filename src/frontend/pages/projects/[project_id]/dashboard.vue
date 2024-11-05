<template>
  <MenuProject>
    <v-card :title="project.name" variant="text">
      <template #append>
        <TagShow :item="project" />
        <TaskButton :project="project" />
        <UtilsButtonEditDelete
          v-if="
            project.owner &&
            (project.owner.id === user.user || user.role === 'Admin')
          "
        >
          <template #edit-dialog="{ isActive }">
            <ProjectEditionDialog
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
        </UtilsButtonEditDelete>
      </template>
      <template #text>
        {{ project.description }}
        <v-divider class="mt-5" />
        <Dashboard />
      </template>
    </v-card>
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

function loadData() {
  api
    .get(route.params.project_id)
    .then((response) => (project.value = response));
}
</script>
