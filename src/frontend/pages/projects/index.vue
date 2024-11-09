<template>
  <NuxtLayout name="header">
    <v-main>
      <Dataset
        ref="dataset"
        :api="api"
        :add="ProjectCreationDialog"
        :filtering="filtering"
        icon="mdi-folder-open"
        empty-head="No Projects"
        :empty-text="
          user.role === 'Admin'
            ? 'Create your first project to start hacking'
            : 'There are no projects yet. Ask your administrator for one'
        "
        @load-data="(data) => (projects = data)"
      >
        <template #data>
          <!-- CODE: review if all Dataset#data starts is within a row and col. If so, move it to Dataset default template -->
          <v-row dense>
            <v-col v-for="project in projects" :key="project.id" cols="4">
              <v-card
                :title="project.name"
                elevation="3"
                class="mx-auto"
                density="compact"
                hover
                :to="`/projects/${project.id}`"
              >
                <template #prepend>
                  <v-avatar color="red-accent-4">
                    <span class="text-h5 text">{{
                      project.name.charAt(0).toUpperCase()
                    }}</span>
                  </v-avatar>
                  <span class="me-2" />
                </template>
                <template #append>
                  <UtilsCounter
                    :collection="project.targets"
                    tooltip="Targets"
                    icon="mdi-target"
                    :link="`/projects/${project.id}/targets`"
                  />
                  <ProjectDefectDojo :project="project" only-link />
                  <UtilsOwner :entity="project" />
                </template>
                <template #text>
                  <v-card-text>
                    <p>{{ project.description }}</p>
                    <TagShow :item="project" divider />
                  </v-card-text>
                </template>
                <v-card-actions @click.stop>
                  <TaskButton
                    v-if="project.targets.length > 0"
                    :project="project"
                  />
                  <v-spacer />

                  <UtilsButtonEditDelete
                    v-if="
                      project.owner.id === user.user || user.role === 'Admin'
                    "
                  >
                    <template #edit-dialog="{ isActive }">
                      <ProjectEditionDialog
                        :api="api"
                        :edit="project"
                        @completed="
                          dataset.loadData(false);
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
                          dataset.loadData(false);
                          isActive.value = false;
                        "
                        @close-dialog="isActive.value = false"
                      />
                    </template>
                  </UtilsButtonEditDelete>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </Dataset>
    </v-main>
  </NuxtLayout>
</template>

<script setup lang="ts">
const dataset = ref(null);
const projects = ref(null);
const user = userStore();
const filters = useFilters();
const api = ref(useApi("/api/projects/", true, "Project"));
const filtering = ref([]);
filters
  .build([
    {
      type: "text",
      label: "Tag",
      icon: "mdi-tag",
      key: "tag",
    },
    {
      type: "switch",
      label: "Mine",
      color: "blue",
      cols: 1,
      key: "owner",
      trueValue: user.user,
      falseValue: null,
      onlyAdmin: true,
    },
    {
      type: "autocomplete",
      label: "Sort",
      icon: "mdi-sort",
      cols: 2,
      collection: ["id", "name"],
      fieldValue: "id",
      fieldTitle: "name",
      key: "ordering",
      defaultValue: "id",
    },
  ])
  .then((results) => (filtering.value = results));

const ProjectCreationDialog = resolveComponent("ProjectCreationDialog");
</script>
