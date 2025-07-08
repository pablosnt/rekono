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
          autz.isAdmin()
            ? 'Create your first project to start hacking'
            : 'There are no projects yet. Ask your administrator to get assigned to one'
        "
        cols="4"
        admin
      >
        <template #item="{ item }">
          <v-card
            :title="item.name"
            elevation="2"
            class="ma-3"
            density="comfortable"
            hover
            :to="
              item.targets.length > 0
                ? `/projects/${item.id}/dashboard`
                : `/projects/${item.id}/targets`
            "
          >
            <template #prepend>
              <v-avatar class="mr-2" color="red-accent-4">
                <span class="text-h5 text">{{
                  item.name.charAt(0).toUpperCase()
                }}</span>
              </v-avatar>
            </template>
            <template #append>
              <UtilsCounterButton
                :collection="item.targets"
                tooltip="Targets"
                icon="mdi-target"
                :link="`/projects/${item.id}/targets`"
              />
              <ProjectDefectDojo :project="item" only-link />
              <UtilsOwner class="ml-4" :entity="item" />
            </template>
            <template #text>
              <v-card-text>
                <p>{{ item.description }}</p>
                <BaseTagShow :tags="item.tags" divider />
              </v-card-text>
            </template>
            <v-card-actions @click.stop>
              <TaskButton
                :project="item"
                :disabled="item.targets.length === 0"
              />
              <v-spacer />
              <UtilsDeleteButtonEdit
                v-if="autz.isOwner(item) || autz.isAdmin()"
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
const autz = useAutz();
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
