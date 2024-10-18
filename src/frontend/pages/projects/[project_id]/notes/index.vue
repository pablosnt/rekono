<!-- eslint-disable vue/no-v-html -->
<template>
  <MenuProject>
    <Dataset
      ref="dataset"
      :api="api"
      :filtering="filtering"
      :add="NoteDialog"
      add-fullscreen
      :default-parameters="{ project: projectId }"
      icon="mdi-notebook"
      empty-head="No Notes"
      empty-text="There are no notes. Create your first one"
      @load-data="(data) => (notes = data)"
    >
      <template #data>
        <v-row dense>
          <!-- todo: Setup the same card height for all of them -->
          <v-col v-for="note in notes" :key="note.id" cols="6">
            <v-card
              :title="note.title"
              :subtitle="new Date(note.updated_at).toUTCString()"
              elevation="3"
              class="mx-auto"
              density="compact"
              :prepend-icon="note.public ? 'mdi-lock-open-variant' : 'mdi-lock'"
              :to="`/projects/${note.project}/notes/${note.id}`"
            >
              <template #append>
                <NoteLink :note="note" />
                <span class="me-2" />
                <UtilsOwner :entity="note" />
                <span class="me-2" />
              </template>
              <template #text>
                <v-container fluid>
                  <div
                    v-if="note.body"
                    style="height: 250px; overflow: hidden"
                    v-html="markdown.render(note.body)"
                  />
                </v-container>
                <TagShow :item="note" :divider="note.body !== null" />
              </template>

              <v-card-actions>
                <NoteForksChip :note="note" />
                <NoteForkedFromLink :note="note" />
                <v-spacer />
                <UtilsButtonLike
                  :api="api"
                  :item="note"
                  @reload="(value) => dataset.loadData(value)"
                />
                <v-speed-dial
                  transition="scale-transition"
                  location="bottom end"
                >
                  <template #activator="{ props: activatorProps }">
                    <v-btn
                      v-bind="activatorProps"
                      size="large"
                      color="grey"
                      icon="mdi-cog"
                      @click.prevent.stop
                    />
                  </template>
                  <v-dialog v-if="!note.forked_from" width="auto">
                    <template #activator="{ props: activatorProps }">
                      <v-btn
                        key="1"
                        :icon="note.public ? 'mdi-share-off' : 'mdi-share'"
                        color="black"
                        v-bind="activatorProps"
                      />
                    </template>
                    <template #default="{ isActive }">
                      <Dialog
                        title="Sharing"
                        :text="
                          note.public
                            ? 'This note won\'t be public anymore and current forks will be unlinked from it'
                            : 'This note will be public so anyone can read and fork it'
                        "
                        :loading="false"
                        color="secondary"
                        width="400"
                        @close-dialog="isActive.value = false"
                      >
                        <template #card>
                          <v-card-actions>
                            <v-btn
                              prepend-icon="mdi-close"
                              color="blue-grey"
                              @click="isActive.value = false"
                              >Cancel</v-btn
                            >
                            <v-spacer />
                            <v-btn
                              :prepend-icon="
                                note.public ? 'mdi-share-off' : 'mdi-share'
                              "
                              color="grey-lighten-5"
                              @click="
                                share(note);
                                isActive.value = false;
                              "
                              >{{ note.public ? "Privatize" : "Share" }}</v-btn
                            >
                          </v-card-actions>
                        </template>
                      </Dialog>
                    </template>
                  </v-dialog>
                  <v-dialog width="500" class="overflow-auto">
                    <template #activator="{ props: activatorProps }">
                      <v-btn
                        key="2"
                        icon="mdi-trash-can-outline"
                        color="red"
                        v-bind="activatorProps"
                      />
                    </template>
                    <template #default="{ isActive }">
                      <UtilsDeleteDialog
                        :id="note.id"
                        :api="api"
                        :text="`Note '${note.title}' will be removed`"
                        @completed="dataset.loadData(false)"
                        @close-dialog="isActive.value = false"
                      />
                    </template>
                  </v-dialog>
                </v-speed-dial>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </Dataset>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
const NoteDialog = resolveComponent("NoteDialog");
const route = useRoute();
const markdown = useMarkdown();
const filters = useFilters();
const projectId = ref(route.params.project_id);
const dataset = ref(null);
const user = userStore();
const notes = ref([]);
const api = useApi("/api/notes/", true, "Note");
const filtering = ref([]);
filters
  .build([
    {
      type: "autocomplete",
      cols: 2,
      label: "Target",
      icon: "mdi-target",
      request: useApi("/api/targets/", true).list({}, true),
      fieldValue: "id",
      fieldTitle: "target",
      key: "related_target",
      callback: (value, definitions) => {
        const tasks = filters.getDefinitionFromKey("related_task", definitions);
        if (value) {
          useApi("/api/tasks/", true)
            .list({ target: value }, true)
            .then((response) => {
              tasks.collection = response.items;
              tasks.disabled = false;
              filters.setValueFromQuery(tasks)
            });
        } else {
          tasks.collection = [];
          tasks.value = null;
          tasks.disabled = true;
        }
      },
    },
    {
      type: "autocomplete",
      cols: 2,
      label: "Scan",
      icon: "mdi-play-network",
      collection: [],
      fieldValue: "id",
      fieldTitle: undefined,
      key: "related_task",

      disabled: true,
    },
    {
      type: "text",
      label: "Tag",
      cols: 2,
      icon: "mdi-tag",
      key: "tag",
    },
    {
      type: "switch",
      label: "Likes",
      color: "red",
      cols: 1,
      key: "like",
      trueValue: true,
      falseValue: null,
    },
    {
      type: "switch",
      label: "Forks",
      color: "blue",
      cols: 1,
      key: "is_fork",
      trueValue: true,
      falseValue: null,
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
      collection: [
        "id",
        "project",
        "target",
        "title",
        "tags",
        "owner",
        "created_at",
        "updated_at",
        "likes_count",
      ],
      fieldValue: "id",
      fieldTitle: "name",
      key: "ordering",
      defaultValue: "-updated_at",
    },
  ])
  .then((results) => (filtering.value = results));

function share(note) {
  const body = {
    title: note.title,
    body: note.body,
    tags: note.tags,
    public: !note.public,
  };
  if (note.target) {
    body.target_id = note.target.id;
  } else if (note.project) {
    body.project_id = note.project.id;
  }
  api.update(body, note.id).then(() => {
    dataset.value.loadData(false);
  });
}
</script>
