<template>
  <CrudPage ref="page" :config="config">
    <template #create-button>
      <NotesButton show />
    </template>
    <template #item="{ item, onDelete }">
      <UPageCard
        :title="item.title"
        :description="getNoteDescription(item)"
        variant="subtle"
        spotlight
        class="cursor-pointer"
        @click="
          navigateTo(`/projects/${route.params.project_id}/notes/${item.id}`)
        "
      >
        <template #leading>
          <!-- TODO: Review the position of the tooltip text everywhere -->
          <UTooltip
            :text="item.public ? 'Public' : 'Private'"
            :content="{ side: 'right', sideOffset: 8, collisionPadding: 8 }"
          >
            <UButton
              :icon="item.public ? 'i-lucide-globe' : 'i-lucide-globe-lock'"
              color="neutral"
              size="xl"
              variant="ghost"
            />
          </UTooltip>
        </template>
        <CrudTags :tags="item.tags" />
        <!-- TODO: Link to the related entity which is not the project one. Top right corner. Requires backend changes -->
        <!-- TODO: Filters by all the related entities -->
        <div class="flex items-center justify-between mt-4" @click.stop>
          <CrudLikes
            size="lg"
            :item-id="item.id"
            endpoint="/api/notes/"
            :liked="item.liked"
            :count="item.likes"
            @update="
              (liked: boolean, count: number) => {
                item.liked = liked;
                item.likes = count;
              }
            "
          />
          <template v-if="userStore.is_auditor">
            <UDropdownMenu
              v-if="userStore.isOwner(item)"
              :items="
                [
                  item.forked_from
                    ? {
                        label: `Forked from #${item.forked_from}`,
                        icon: 'i-lucide-link',
                        color: 'neutral',
                        to: `/projects/${$route.params.project_id}/notes/${item.forked_from}`,
                      }
                    : {
                        label: item.public ? 'Make private' : 'Publish',
                        icon: item.public
                          ? 'i-lucide-globe-lock'
                          : 'i-lucide-globe',
                        color: item.public ? 'neutral' : 'warning',
                        onSelect: () => switchVisibility(item),
                      },
                  {
                    label: 'Delete',
                    icon: 'i-lucide-trash',
                    color: 'error',
                    onSelect: onDelete,
                  },
                ].filter((i) => Object.keys(i).length > 0)
              "
              @click.stop
            >
              <UButton
                icon="i-lucide-more-horizontal"
                variant="ghost"
                color="neutral"
                @click.stop
              />
            </UDropdownMenu>
            <UButton
              v-else
              icon="i-lucide-git-fork"
              color="neutral"
              variant="subtle"
              :label="`${item.forks.length} Forks`"
              @click="
                api.create(`${item.id}/fork/`, {}).then(() => {
                  page.fetch();
                  toast.add({
                    title: 'Note Forked',
                    description: `Note '${item.title}' has been forked`,
                    color: 'success',
                  });
                })
              "
            />
          </template>
        </div>
      </UPageCard>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import type { CrudConfig, FilterOption } from "~/types/crud";
import { useUserStore } from "~/store/user";
import type { Note } from "~/types/models";
import { useTimeAgo } from "@vueuse/core";

definePageMeta({ layout: "project" });

const userStore = useUserStore();
const backend = useBackend();
const route = useRoute();
const toast = useToast();
const api = useApi("/api/notes/");
const page = ref();
const userOptions = ref<FilterOption[]>([]);

function getNoteDescription(note: Note): string {
  const created_ago = useTimeAgo(new Date(note.created_at)).value;
  const updated_ago = useTimeAgo(new Date(note.updated_at)).value;
  return `Created ${created_ago} by @${note.owner.username}${created_ago === updated_ago ? "" : `. Updated ${updated_ago}`}`;
}

function switchVisibility(note: Note) {
  api
    .update(`${note.id}/`, {
      project: note.project,
      target: note.target,
      task: note.task,
      osint: note.osint,
      host: note.host,
      port: note.port,
      path: note.path,
      credential: note.credential,
      technology: note.technology,
      vulnerability: note.vulnerability,
      exploit: note.exploit,
      title: note.title,
      body: note.body,
      tags: note.tags,
      public: !note.public,
    })
    .then((response) => {
      note.public = !note.public;
    });
}

const config: CrudConfig<Note> = reactive({
  endpoint: "/api/notes/",
  entityName: "Note",
  entityNamePlural: "Notes",
  icon: "i-lucide-notebook",
  useGrid: true,
  searchable: true,
  searchPlaceholder: "Search notes...",
  get filters() {
    return [
      {
        key: "tag",
        label: "Tag",
        icon: "i-lucide-tag",
        type: "text" as const,
      },
      {
        key: "owner",
        label: "Owner",
        icon: "i-lucide-user",
        type: "select" as const,
        options: userOptions,
      },
      {
        key: "public",
        label: "Public",
        type: "checkbox" as const,
      },
      {
        key: "is_fork",
        label: "Forks",
        type: "checkbox" as const,
      },
      {
        key: "like",
        label: "Favourites",
        icon: "i-lucide-heart",
        type: "checkbox" as const,
      },
    ];
  },
  ordering: [
    "id",
    "title",
    "tags",
    "owner",
    { id: "created_at", label: "Created" },
    { id: "updated_at", label: "Updated" },
    { id: "likes_count", label: "Likes" },
  ],
  defaultOrdering: "-id",
  defaultFilters: { project: route.params.project_id },
  defaultBody: { project: route.params.project_id },
  deleteMessage: (note: Note) => [
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
        description: note.title,
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
  ],
  canRead: true,
  canCreate: userStore.is_auditor,
  canEdit: false,
  canDelete: (note: Note) => userStore.isOwner(note),
});

onMounted(() => {
  backend.getUserOptions(userOptions, { role: "Admin", is_active: true });
  backend.getUserOptions(userOptions, { role: "Auditor", is_active: true });
});
</script>
