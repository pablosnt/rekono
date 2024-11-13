<template>
  <NuxtLayout name="main">
    <v-main>
      <Dataset
        ref="dataset"
        :api="api"
        :add="ProjectDialogCreate"
        :filtering="filtering"
        icon="mdi-folder-open"
        empty-head="No Projects"
        :empty-text="
          user.role === 'Admin'
            ? 'Create your first project to start hacking'
            : 'There are no projects yet. Ask your administrator for one'
        "
        cols="4"
      >
        <template #item="{ item }">
          <v-card
            :title="item.name"
            elevation="3"
            class="mx-auto"
            density="compact"
            hover
            :to="`/projects/${item.id}`"
          >
            <template #prepend>
              <v-avatar color="red-accent-4">
                <span class="text-h5 text">{{
                  item.name.charAt(0).toUpperCase()
                }}</span>
              </v-avatar>
              <span class="me-2" />
            </template>
            <template #append>
              <UtilsCounterButton
                :collection="item.targets"
                tooltip="Targets"
                icon="mdi-target"
                :link="`/projects/${item.id}/targets`"
              />
              <ProjectDefectDojo :project="item" only-link />
              <UtilsOwner :entity="item" />
            </template>
            <template #text>
              <v-card-text>
                <p>{{ item.description }}</p>
                <BaseTagShow :tags="item.tags" divider />
              </v-card-text>
            </template>
            <v-card-actions @click.stop>
              <TaskButton v-if="item.targets.length > 0" :project="item" />
              <v-spacer />

              <UtilsDeleteButtonEdit
                v-if="item.owner.id === user.user || user.role === 'Admin'"
              >
                <template #edit-dialog="{ isActive }">
                  <ProjectDialogEdit
                    :api="api"
                    :edit="item"
                    @completed="
                      dataset.loadData(false);
                      isActive.value = false;
                    "
                    @close-dialog="isActive.value = false"
                  />
                </template>
                <template #delete-dialog="{ isActive }">
                  <UtilsDeleteDialog
                    :id="item.id"
                    :api="api"
                    :text="`Project '${item.name}' will be removed`"
                    @completed="
                      dataset.loadData(false);
                      isActive.value = false;
                    "
                    @close-dialog="isActive.value = false"
                  />
                </template>
              </UtilsDeleteButtonEdit>
            </v-card-actions>
          </v-card>
        </template>
      </Dataset>
    </v-main>
  </NuxtLayout>
</template>

<script setup lang="ts">
const dataset = ref(null);
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

const ProjectDialogCreate = resolveComponent("ProjectDialogCreate");
</script>
