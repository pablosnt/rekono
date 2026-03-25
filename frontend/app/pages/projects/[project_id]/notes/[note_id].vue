<template>
  <UForm
    v-if="note"
    ref="noteForm"
    class="space-y-4 p-3"
    :schema="schema"
    :state="noteState"
    :validate-on="['input', 'change']"
  >
    <div
      class="flex flex-row flex-wrap items-center justify-between gap-4 w-full"
    >
      <div class="flex flex-row justify-start items-center gap-4">
        <UFormField name="title">
          <UInput
            v-model="note.title"
            class="w-full min-w-64"
            placeholder="Title"
            required
            type="text"
            variant="ghost"
            size="xl"
            :disabled="!canEdit"
            :ui="{ base: 'text-4xl font-bold' }"
          />
        </UFormField>
      </div>
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
          v-else-if="!canEdit"
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
              navigateTo(
                `/projects/${$route.params.project_id}/notes/${response.id}`,
              );
            })
          "
        />
        <CrudLikes
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
              label: note.public ? 'Make private' : 'Publish',
              icon: note.public ? 'i-lucide-globe-lock' : 'i-lucide-globe',
              color: note.public ? 'neutral' : 'warning',
              onSelect: () => {
                note.public = !note.public;
                updateNote();
              },
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
            variant="ghost"
            color="neutral"
          />
        </UDropdownMenu>
        <CrudDeleteModal
          :open="deleteOpen"
          :item="note"
          :config="deleteConfig"
          :api="api"
          @open="(open) => (deleteOpen = open)"
          @deleted="navigateTo(`/projects/${$route.params.project_id}/notes`)"
        />
      </div>
    </div>
    <UFormField v-if="canEdit" name="tags">
      <CrudTagsForm v-model="note.tags" @update:model-value="updateNote()" />
    </UFormField>
    <CrudTags v-else class="ml-3" :tags="note.tags" />
    <UEditor
      v-slot="{ editor }"
      v-model="note.body"
      placeholder="Type / for commands..."
      content-type="markdown"
      :mention="false"
      :editable="canEdit"
      class="w-full"
      :starter-kit="{
        blockquote: true,
        link: {
          openOnClick: true,
        },
      }"
      @update:model-value="updateNote"
    >
      <UEditorDragHandle :editor="editor" />
      <!-- TODO: https://ui.nuxt.com/docs/components/editor-drag-handle#with-dropdown-menu -->
      <!-- TODO: https://ui.nuxt.com/docs/components/editor-drag-handle#with-dropdown-menu -->
      <UEditorEmojiMenu
        :editor="editor"
        :items="gitHubEmojis"
        :append-to="appendToBody"
      />
      <UEditorSuggestionMenu
        :editor="editor"
        :items="[
          [
            { type: 'label', label: 'Text' },
            { kind: 'paragraph', label: 'Paragraph', icon: 'i-lucide-type' },
            {
              kind: 'heading',
              level: 1,
              label: 'Heading 1',
              icon: 'i-lucide-heading-1',
            },
            {
              kind: 'heading',
              level: 2,
              label: 'Heading 2',
              icon: 'i-lucide-heading-2',
            },
            {
              kind: 'heading',
              level: 3,
              label: 'Heading 3',
              icon: 'i-lucide-heading-3',
            },
            {
              kind: 'heading',
              level: 4,
              label: 'Heading 4',
              icon: 'i-lucide-heading-4',
            },
          ],
          [
            { type: 'label', label: 'Lists' },
            {
              kind: 'bulletList',
              label: 'Bullet List',
              icon: 'i-lucide-list',
            },
            {
              kind: 'orderedList',
              label: 'Numbered List',
              icon: 'i-lucide-list-ordered',
            },
            {
              kind: 'taskList',
              label: 'To-Do List',
              icon: 'i-lucide-list-todo',
            },
          ],
          [
            { type: 'label', label: 'Insert' },
            { kind: 'imageUpload', icon: 'i-lucide-image', label: 'Image' },
            {
              kind: 'blockquote',
              label: 'Blockquote',
              icon: 'i-lucide-text-quote',
            },
            {
              kind: 'codeBlock',
              label: 'Code Block',
              icon: 'i-lucide-square-code',
            },
            { kind: 'link', label: 'Link', icon: 'i-lucide-link' },
            {
              kind: 'horizontalRule',
              label: 'Divider',
              icon: 'i-lucide-separator-horizontal',
            },
          ],
        ]"
        :append-to="appendToBody"
      />
      <UEditorToolbar
        :editor="editor"
        :items="[
          [
            {
              icon: 'i-lucide-text',
              content: { align: 'start' },
              items: [
                {
                  kind: 'paragraph',
                  label: 'Paragraph',
                  icon: 'i-lucide-type',
                },
                {
                  kind: 'heading',
                  level: 1,
                  icon: 'i-lucide-heading-1',
                  label: 'Heading 1',
                },
                {
                  kind: 'heading',
                  level: 2,
                  icon: 'i-lucide-heading-2',
                  label: 'Heading 2',
                },
                {
                  kind: 'heading',
                  level: 3,
                  icon: 'i-lucide-heading-3',
                  label: 'Heading 3',
                },
                {
                  kind: 'heading',
                  level: 4,
                  icon: 'i-lucide-heading-4',
                  label: 'Heading 4',
                },
              ],
            },
          ],
          [
            { kind: 'mark', mark: 'bold', icon: 'i-lucide-bold' },
            { kind: 'mark', mark: 'italic', icon: 'i-lucide-italic' },
            { kind: 'mark', mark: 'underline', icon: 'i-lucide-underline' },
            { kind: 'mark', mark: 'strike', icon: 'i-lucide-strikethrough' },
            { kind: 'mark', mark: 'code', icon: 'i-lucide-code' },
          ],
          [
            { kind: 'textAlign', align: 'left', icon: 'i-lucide-align-left' },
            {
              kind: 'textAlign',
              align: 'center',
              icon: 'i-lucide-align-center',
            },
            {
              kind: 'textAlign',
              align: 'right',
              icon: 'i-lucide-align-right',
            },
          ],
          [
            { kind: 'bulletList', icon: 'i-lucide-list' },
            { kind: 'orderedList', icon: 'i-lucide-list-ordered' },
            { kind: 'taskList', icon: 'i-lucide-list-todo' },
          ],
          [
            { kind: 'imageUpload', icon: 'i-lucide-image' },
            { kind: 'codeBlock', icon: 'i-lucide-file-code' },
            { kind: 'mark', mark: 'link', icon: 'i-lucide-link' },
          ],
          [
            { kind: 'undo', icon: 'i-lucide-undo' },
            { kind: 'redo', icon: 'i-lucide-redo' },
          ],
        ]"
        class="border border-muted py-2 px-8 sm:px-16 overflow-x-auto mb-5"
      />
      <!-- TODO: https://ui.nuxt.com/docs/components/editor-toolbar#items -->
      <!-- TODO: https://ui.nuxt.com/docs/components/editor-toolbar#layout -->
      <!-- TODO: https://ui.nuxt.com/docs/components/editor-toolbar#with-link-popover -->
    </UEditor>
  </UForm>
</template>

<script setup lang="ts">
import type { Note } from "~/types/models";
import { gitHubEmojis } from "@tiptap/extension-emoji";
import { useUserStore } from "~/store/user";
import * as z from "zod";

definePageMeta({ layout: "project" });
const route = useRoute();
const userStore = useUserStore();
const toast = useToast();
const backend = useBackend();
const api = useApi("/api/notes/");
const validation = useValidation();
const note = ref();
const canEdit = ref(false);
const deleteOpen = ref(false);
const noteForm = ref();
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
  deleteMessage: () => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this note?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        get description() {
          return note.value?.title;
        },
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
  ],
};
const currentNote = useState<Note | null>("currentNote", () => null);
const appendToBody = import.meta.client ? () => document.body : undefined;

function fetchNote() {
  api.get(`${route.params.note_id}/`).then((response) => {
    response.related_entity = backend.getNoteRelatedEntity(response);
    note.value = response;
    currentNote.value = response;
    canEdit.value = userStore.isOwner(note.value);
  });
}

function updateNote() {
  if (!schema.safeParse(noteState.value).success) return;
  api
    .update(`${route.params.note_id}/`, {
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
    })
    .then((response) => {
      if (response.title !== currentNote.value.title) {
        currentNote.value = response;
      }
    });
}

onMounted(fetchNote);
</script>
