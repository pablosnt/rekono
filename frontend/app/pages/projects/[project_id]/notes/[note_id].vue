<template>
  <UForm
    v-if="note"
    class="space-y-4 p-3"
    :schema="schema"
    :state="noteState"
    :validate-on="['input', 'change']"
  >
    <div
      class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between w-full"
    >
      <UFormField name="title" class="flex-1 min-w-0">
        <UInput
          v-model="note.title"
          class="w-full"
          placeholder="Title"
          required
          type="text"
          variant="ghost"
          size="xl"
          aria-label="Title"
          :disabled="!canEdit"
          :ui="{ base: 'text-4xl font-bold' }"
          @update:model-value="updateNote()"
        />
      </UFormField>
      <div class="flex flex-wrap items-center gap-3">
        <UButton
          v-if="note.related_entity"
          :icon="note.related_entity.icon"
          :to="note.related_entity.to"
          :label="note.related_entity.label"
          color="primary"
          variant="ghost"
        />
        <UButton
          v-if="note.forked"
          icon="i-lucide-git-fork"
          color="neutral"
          variant="solid"
          :label="`${note.forks.length} Forks`"
          :to="`/projects/${$route.params.project_id}/notes/${note.forked}`"
        />
        <UButton
          v-else-if="note.forked_from"
          icon="i-lucide-git-fork"
          color="neutral"
          variant="subtle"
          :label="`Forked from #${note.forked_from}`"
          :to="`/projects/${$route.params.project_id}/notes/${note.forked_from}`"
        />
        <UButton
          v-else-if="!canEdit && userStore.is_auditor"
          icon="i-lucide-git-fork"
          color="neutral"
          variant="subtle"
          :label="`${note.forks.length} Forks`"
          @click="
            api.create(`${note.id}/fork/`, {}).then((response) => {
              toast.add({
                title: 'Note Forked',
                description: `Note '${note.title}' has been forked`,
                color: 'success',
              });
              createdNote = response;
              navigateTo(
                `/projects/${$route.params.project_id}/notes/${response.id}`,
              );
            })
          "
        />
        <UButton
          v-if="canEdit"
          as="span"
          icon="i-lucide-git-fork"
          color="neutral"
          variant="subtle"
          size="lg"
          :label="`${note.forks.length} Forks`"
          class="pointer-events-none"
        />
        <Likes
          size="lg"
          :item-id="note.id"
          endpoint="/api/notes/"
          :liked="note.liked"
          :count="note.likes"
          @update="
            (liked: boolean, count: number) => {
              note.liked = liked;
              note.likes = count;
            }
          "
        />
        <UDropdownMenu
          v-if="canEdit"
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
            aria-label="Note actions"
          />
        </UDropdownMenu>
        <LazyCrudDeleteModal
          :open="deleteOpen"
          :item="note"
          :config="deleteConfig"
          :api="api"
          @open="(open) => (deleteOpen = open)"
          @deleted="navigateTo(`/projects/${$route.params.project_id}/notes`)"
        />
      </div>
    </div>
    <div class="flex items-center gap-4 text-sm text-muted flex-wrap">
      <span
        v-if="!canEdit && note.updated_at"
        class="flex items-center gap-1.5"
      >
        <UIcon name="i-lucide-clock-4" class="size-3 shrink-0" />
        {{
          new Date(note.updated_at).toLocaleString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })
        }}
      </span>
      <UButton
        v-if="canEdit"
        :label="note.public ? 'Public' : 'Private'"
        :color="note.public ? 'warning' : 'neutral'"
        :icon="note.public ? 'i-lucide-globe' : 'i-lucide-lock'"
        variant="subtle"
        size="xs"
        :disabled="note.forked_from"
        @click="
          note.public = !note.public;
          updateNote();
        "
      />
      <span v-else-if="note.owner?.username" class="flex items-center gap-1.5">
        <UIcon name="i-lucide-user" class="size-3 shrink-0" />
        {{ note.owner.username }}
      </span>
      <span v-if="note.body.length > 0" class="flex items-center gap-1.5">
        <UIcon name="i-lucide-file-text" class="size-3 shrink-0" />
        {{ note.body?.match(/[a-zA-Z0-9\u00C0-\u024F]+/g)?.length ?? 0 }} words
      </span>
      <Tags v-if="!canEdit && note.tags?.length" :tags="note.tags" />
    </div>
    <UFormField v-if="canEdit" class="mt-5" name="tags">
      <TagsForm v-model="note.tags" @update:model-value="updateNote()" />
    </UFormField>
    <USeparator class="mb-6 mt-6" />
    <NotesEditor
      v-model="note.body"
      :entity-id="note.id"
      :can-edit="canEdit"
      @update:model-value="updateNote"
    />
  </UForm>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import type { Note } from "~/types/models";
import * as z from "zod";

const route = useRoute();
const userStore = useUserStore();
const toast = useToast();
const api = useApi("/api/notes/");
const validation = useValidation();
const createdNote = useState<Note | null>("created-note", () => null);
const note = ref();
const canEdit = ref(false);
const deleteOpen = ref(false);
const schema = z.object({
  title: validation.name("title"),
  tags: z.array(validation.name("tag", true, 100)).optional(),
});
const noteState = computed(() => ({
  title: note.value?.title,
  tags: note.value?.tags ?? [],
}));
const deleteConfig = {
  entityName: "Note",
  deleteMessage: () => buildDeleteMessage("note", note.value?.title),
};

function applyNote(response: Note) {
  note.value = response;
  note.value.related_entity = getNoteRelatedEntity(response);
  canEdit.value = userStore.isOwner(note.value);
  createdNote.value = null;
}

function fetchNote() {
  if (
    createdNote.value &&
    String(createdNote.value.id) === String(route.params.note_id)
  ) {
    applyNote(createdNote.value);
  } else {
    api.get(`${route.params.note_id}/`).then(applyNote);
  }
}

function updateNote() {
  if (!schema.safeParse(noteState.value).success) return;
  api.update(`${route.params.note_id}/`, {
    project: note.value?.project,
    target_id: note.value?.target?.id,
    task_id: note.value?.task?.id,
    osint_id: note.value?.osint?.id,
    host_id: note.value?.host?.id,
    port_id: note.value?.port?.id,
    path_id: note.value?.path?.id,
    credential_id: note.value?.credential?.id,
    technology_id: note.value?.technology?.id,
    vulnerability_id: note.value?.vulnerability?.id,
    exploit_id: note.value?.exploit?.id,
    title: note.value?.title,
    body: note.value?.body,
    tags: note.value?.tags,
    public: note.value?.public,
  });
}

onMounted(fetchNote);
</script>
