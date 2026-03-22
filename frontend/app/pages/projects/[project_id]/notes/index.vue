<template>
  <CrudPage
    ref="page"
    :config="config"
    @fetched="
      (items) =>
        items.forEach((item) => (item.related_entity = getRelatedEntity(item)))
    "
  >
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
        <CrudTags :tags="item.tags" />
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
                apiNotes.create(`${item.id}/fork/`, {}).then(() => {
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
const api = useApi("/api/");
const apiNotes = useApi("/api/notes/");
const page = ref();
const userOptions = ref<FilterOption[]>([]);
const targetOptions = ref();
const taskOptions = ref();
const osintOptions = ref();
const hostOptions = ref();
const portOptions = ref();
const credentialOptions = ref();
const technologyOptions = ref();
const vulnerabilityOptions = ref();
const exploitOptions = ref();

function getNoteDescription(note: Note): string {
  const created_ago = useTimeAgo(new Date(note.created_at)).value;
  const updated_ago = useTimeAgo(new Date(note.updated_at)).value;
  return `Created ${created_ago} by @${note.owner.username}${created_ago === updated_ago ? "" : `. Updated ${updated_ago}`}`;
}

function getRelatedEntity(
  note: Note,
): Record<string, string | undefined> | null {
  const baseTo = `/projects/${route.params.project_id}/`;
  for (const definition of [
    {
      entity: note.exploit,
      to: note.exploit?.vulnerability
        ? `${baseTo}vulnerabilities/${note.exploit?.vulnerability}`
        : note.exploit?.technology?.port?.host?.id
          ? `${baseTo}assets/${note.exploit?.technology?.port?.host?.id}`
          : undefined,
      label: note.exploit?.title,
      icon: "i-lucide-flame",
    },
    {
      entity: note.vulnerability,
      to: `${baseTo}vulnerabilities/${note.vulnerability?.id}`,
      label: note.vulnerability?.name,
      icon: "i-lucide-bug",
    },
    // todo: We might have to include credentials on the technologies page, instead of on a custom view. If so, we can split the views on OSINT, Assets and Vulnerabilities
    {
      entity: note.credential,
      to: `${baseTo}/credentials/${note.credential?.id}`,
      icon: "i-lucide-key",
      label:
        note.credential?.username ||
        note.credential?.email ||
        `#${note.credential?.id}`,
    },
    {
      entity: note.technology,
      to: note.technology?.port?.host?.id
        ? `${baseTo}assets/${note.technology?.port?.host?.id}`
        : undefined,
      label: note.technology?.name,
      icon: "i-lucide-code",
    },
    {
      entity: note.path,
      to: note.path?.port?.host?.id
        ? `${baseTo}assets/${note.path?.port?.host?.id}`
        : undefined,
      label: note.path?.path,
      icon: "i-lucide-slash",
    },
    {
      entity: note.port,
      to: `${baseTo}/assets/${note.port?.host}`,
      icon: "i-lucide-keethernet-porty",
      label: `${note.port?.host?.ip}:${note.port?.port}`,
    },
    {
      entity: note.host,
      to: `${baseTo}/assets/${note.host?.id}`,
      icon: "i-lucide-server",
      label: note.host?.ip,
    },
    {
      entity: note.osint,
      to: `${baseTo}/osint/${note.osint?.id}`,
      icon: "i-lucide-rss",
      label: note.osint?.data,
    },
    {
      entity: note.task,
      to: `${baseTo}/scans/${note.task?.id}`,
      icon: "i-lucide-play",
      label: note.task?.process
        ? note.task.process.name
        : note.task?.configuration?.tool.name,
    },
    {
      entity: note.target,
      to: `${baseTo}/targets/${note.target?.id}`,
      icon: note.target
        ? backend.targetTypes.find((t) => t.value === note.target?.type)?.icon
        : "i-lucide-locate-fixed",
      label: note.target?.target,
    },
  ]) {
    if (definition.entity) {
      return {
        to: definition.to,
        icon: definition.icon,
        label: definition.label || "",
      };
    }
  }
  return null;
}

function switchVisibility(note: Note) {
  apiNotes
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
  // TODO: Test that all the new filters are loaded correctly and are working
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
      {
        key: "related_target",
        label: "Target",
        icon: "i-lucide-locate-fixed",
        type: "select" as const,
        options: targetOptions,
      },
      {
        key: "related_task",
        label: "Scan",
        icon: "i-lucide-play",
        type: "select" as const,
        options: taskOptions,
      },
      {
        key: "related_host",
        label: "Host",
        icon: "i-lucide-server",
        type: "select" as const,
        options: hostOptions,
      },
      {
        key: "related_port",
        label: "Port",
        icon: "i-lucide-ethernet-port",
        type: "select" as const,
        options: portOptions,
      },
      {
        key: "related_technology",
        label: "Technology",
        icon: "i-lucide-code",
        type: "select" as const,
        options: technologyOptions,
      },
      {
        key: "credential",
        label: "Credential",
        icon: "i-lucide-key",
        type: "select" as const,
        options: credentialOptions,
      },
      {
        key: "related_vulnerability",
        label: "Vulnerability",
        icon: "i-lucide-bug",
        type: "select" as const,
        options: vulnerabilityOptions,
      },
      {
        key: "exploit",
        label: "Exploit",
        icon: "i-lucide-flame",
        type: "select" as const,
        options: exploitOptions,
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

function getFindingOptions(
  endpoint: string,
  variable: Ref,
  parser: (i: unknown) => unknown,
) {
  api
    .list(endpoint, { project: route.params.project_id }, true)
    .then(
      (response) => (variable.value = response.items.map((i) => parser(i))),
    );
}

onMounted(() => {
  backend.getUserOptions(userOptions, { role: "Admin", is_active: true });
  backend.getUserOptions(userOptions, { role: "Auditor", is_active: true });
  backend.getTargetOptions(targetOptions, { project: route.params.project_id });
  backend.getTaskOptions(taskOptions, { project: route.params.project_id });
  // todo: Ellaborate options more with icons, avatars, etc and define types
  getFindingOptions("osint/", osintOptions, (osint) => {
    return { label: osint.data, value: osint.id };
  });
  getFindingOptions("hosts/", hostOptions, (host) => {
    return { label: host.ip, value: host.id };
  });
  getFindingOptions("ports/", portOptions, (port) => {
    return {
      label: port.host ? `${port.host?.ip}:${port.port}` : port.port.toString(),
      value: port.id,
    };
  });
  getFindingOptions("technologies/", technologyOptions, (technology) => {
    return {
      label: technology.version
        ? `${technology.name} ${technology.version}`
        : technology.name,
      value: technology.id,
    };
  });
  getFindingOptions("credentials/", credentialOptions, (credential) => {
    return {
      label:
        credential.email ||
        credential.username ||
        `Credential #${credential.id}`,
      value: credential.id,
    };
  });
  getFindingOptions(
    "vulnerabilities/",
    vulnerabilityOptions,
    (vulnerability) => {
      return { label: vulnerability.name, value: vulnerability.id };
    },
  );
  getFindingOptions("exploits/", exploitOptions, (exploit) => {
    return { label: exploit.title, value: exploit.id };
  });
});
</script>
