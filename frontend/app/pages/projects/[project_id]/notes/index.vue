<template>
  <CrudPage
    ref="page"
    :config="config"
    :on-create="() => notesButton?.createNote()"
    @fetched="
      (items) =>
        items.forEach(
          (item) => (item.related_entity = getNoteRelatedEntity(item)),
        )
    "
  >
    <template #create-button>
      <NotesButton ref="notesButton" show />
    </template>
    <template #item="{ item, onDelete }">
      <UPageCard
        :title="item.title"
        :description="getNoteDescription(item)"
        variant="subtle"
        spotlight
        class="cursor-pointer"
        :ui="{ leading: 'flex w-full items-center justify-between mb-2.5' }"
        @click="
          navigateTo(`/projects/${route.params.project_id}/notes/${item.id}`)
        "
      >
        <template #leading>
          <UTooltip
            :text="item.public ? 'Public' : 'Private'"
            :content="{ side: 'right', sideOffset: 8, collisionPadding: 8 }"
          >
            <UButton
              :icon="item.public ? 'i-lucide-globe' : 'i-lucide-globe-lock'"
              color="neutral"
              size="xl"
              variant="ghost"
              :aria-label="item.public ? 'Public note' : 'Private note'"
            />
          </UTooltip>
          <UButton
            v-if="item.related_entity"
            :icon="item.related_entity.icon"
            :to="item.related_entity.to"
            :label="item.related_entity.label"
            color="primary"
            variant="ghost"
            @click.stop
          />
        </template>
        <Tags :tags="item.tags" />
        <div class="flex items-center justify-between mt-4" @click.stop>
          <Likes
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
              :items="[
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
              ]"
              @click.stop
            >
              <UButton
                icon="i-lucide-more-horizontal"
                variant="ghost"
                color="neutral"
                aria-label="Note actions"
                @click.stop
              />
            </UDropdownMenu>
            <UButton
              v-else
              icon="i-lucide-git-fork"
              color="neutral"
              :variant="item.forked ? 'solid' : 'subtle'"
              :label="`${item.forks.length} Forks`"
              :to="
                item.forked
                  ? `/projects/${$route.params.project_id}/notes/${item.forked}`
                  : undefined
              "
              @click="
                item.forked
                  ? undefined
                  : api.create(`${item.id}/fork/`, {}).then(() => {
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

const userStore = useUserStore();
const options = useOptions();
const route = useRoute();
const toast = useToast();
const api = useApi("/api/notes/");
const page = ref();
const notesButton = ref();
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
      target_id: note.target?.id,
      task_id: note.task?.id,
      osint_id: note.osint?.id,
      host_id: note.host?.id,
      port_id: note.port?.id,
      path_id: note.path?.id,
      credential_id: note.credential?.id,
      technology_id: note.technology?.id,
      vulnerability_id: note.vulnerability?.id,
      exploit_id: note.exploit?.id,
      title: note.title,
      body: note.body,
      tags: note.tags,
      public: !note.public,
    })
    .then(() => {
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
  acceptedFilters: [
    {
      key: "related_target",
      label: "Target",
      icon: "i-lucide-locate-fixed",
      loadOption: (value) => options.target(value),
    },
    {
      key: "related_task",
      label: "Scan",
      icon: "i-lucide-play",
      loadOption: (value) => options.task(value),
    },
    {
      key: "related_host",
      label: "Host",
      icon: "i-lucide-server",
      loadOption: (value) => options.host(value),
    },
    {
      key: "related_port",
      label: "Port",
      icon: "i-lucide-ethernet-port",
      loadOption: (value) => options.port(value),
    },
    {
      key: "related_technology",
      label: "Technology",
      icon: "i-lucide-code",
      loadOption: (value) => options.technology(value),
    },
    {
      key: "credential",
      label: "Credential",
      icon: "i-lucide-key",
      loadOption: (value) => options.credential(value),
    },
    {
      key: "related_vulnerability",
      label: "Vulnerability",
      icon: "i-lucide-bug",
      loadOption: (value) => options.vulnerability(value),
    },
    {
      key: "exploit",
      label: "Exploit",
      icon: "i-lucide-flame",
      loadOption: (value) => options.exploit(value),
    },
  ],
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
  deleteMessage: (note: Note) => buildDeleteMessage("note", note.title),
  canRead: true,
  canCreate: userStore.is_auditor,
  canEdit: false,
  canDelete: (note: Note) => userStore.isOwner(note),
});

onMounted(() => {
  options.users(userOptions, { role: "Admin", is_active: true });
  options.users(userOptions, { role: "Auditor", is_active: true });
});
</script>
