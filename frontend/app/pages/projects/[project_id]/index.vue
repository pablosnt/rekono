<template>
  <div v-if="currentProject">
    <UForm
      class="space-y-4 p-3"
      :schema="schema"
      :state="state"
      :validate-on="['input', 'change']"
    >
      <div
        class="flex flex-row flex-wrap items-center justify-between w-full gap-2"
      >
        <UFormField name="name" class="flex-1 min-w-0">
          <UInput
            v-model="state.name"
            class="w-full"
            placeholder="Name"
            required
            type="text"
            variant="ghost"
            size="xl"
            aria-label="Name"
            :disabled="!userStore.is_admin"
            :ui="{ base: 'text-4xl font-bold' }"
            @update:model-value="update()"
          />
        </UFormField>
        <div class="flex flex-wrap items-center gap-3">
          <DefectdojoModal
            :sync="currentProject.defectdojo_sync"
            @update="fetch()"
          />
          <UDropdownMenu
            v-if="userStore.is_admin"
            :items="[
              {
                label: 'Copy link',
                icon: 'i-lucide-copy',
                onSelect: copyLink,
              },
              {
                label: 'Delete',
                icon: 'i-lucide-trash',
                color: 'error',
                onSelect: () => (deleteOpen = true),
              },
            ]"
          >
            <UButton
              icon="i-lucide-more-horizontal"
              variant="subtle"
              color="neutral"
              aria-label="Project actions"
            />
          </UDropdownMenu>
          <CrudDeleteModal
            :open="deleteOpen"
            :item="currentProject"
            :config="deleteConfig"
            :api="api"
            @open="(open) => (deleteOpen = open)"
            @deleted="navigateTo('/projects')"
          />
        </div>
      </div>
      <UFormField v-if="userStore.is_admin" class="mt-5" name="tags">
        <CrudTagsForm v-model="state.tags" @update:model-value="update()" />
      </UFormField>
      <CrudTags
        v-else-if="currentProject.tags.length"
        :tags="currentProject.tags"
      />
      <UFormField class="mt-8" name="description">
        <UTextarea
          v-model="state.description"
          class="w-full"
          :rows="10"
          placeholder="Project description..."
          autoresize
          color="neutral"
          aria-label="Description"
          :disabled="!userStore.is_admin"
        />
      </UFormField>
    </UForm>
    <div v-if="currentProject.targets.length > 0">
      <USeparator class="mb-8 mt-8" />
      <FindingsCounterAll :project-id="route.params.project_id" only-active />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const api = useApi("/api/projects/");
const route = useRoute();
const userStore = useUserStore();
const config = useProjectsConfig();
const { currentProject, setCurrentProject } = useCurrentProject();
const schema = config.formSchema;
const state = ref({});
const initializedProjectId = ref(null);
const deleteOpen = ref(false);
const deleteConfig = {
  entityName: "Project",
  deleteMessage: config.deleteMessage,
};

function fetch() {
  api.get(`${route.params.project_id}/`).then((response) => {
    setCurrentProject(response);
  });
}

function update() {
  if (!schema.safeParse(state.value).success) return;
  api.update(`${route.params.project_id}/`, state.value).then((response) => {
    setCurrentProject(response);
  });
}

watch(
  currentProject,
  (data) => {
    if (!data || data.id === initializedProjectId.value) return;
    state.value = {
      name: data.name,
      description: data.description,
      tags: data.tags ?? [],
    };
    initializedProjectId.value = data.id;
  },
  { immediate: true, flush: "sync" },
);
</script>
