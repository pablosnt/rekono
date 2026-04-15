<template>
  <Panel :navigation-items="items" storage-key="project-panel">
    <template
      #panel-header="{ sidebarCollapsed, largeScreen, switchCollapsed }"
    >
      <div class="relative flex items-center w-full justify-between">
        <div
          v-if="!sidebarCollapsed"
          class="flex items-center justify-center gap-2"
        >
          <UAvatar
            :text="projectEntity.name.charAt(0).toUpperCase()"
            class="bg-primary-500"
            :ui="{ fallback: 'text-white' }"
            width="30"
          />
          <h1>{{ projectEntity.name }}</h1>
        </div>
        <UAvatar
          v-else
          :text="projectEntity.name.charAt(0).toUpperCase()"
          width="30"
          class="bg-primary-500 opacity-100 group-hover:opacity-0 transition-opacity duration-200"
          :ui="{ fallback: 'text-white' }"
        />
        <UButton
          v-if="largeScreen"
          :icon="
            sidebarCollapsed
              ? 'i-lucide-chevrons-right'
              : 'i-lucide-chevrons-left'
          "
          color="neutral"
          variant="ghost"
          :class="
            'ml-auto opacity-0 group-hover:opacity-100 transition-opacity duration-200' +
            (sidebarCollapsed ? ' absolute' : '')
          "
          @click="switchCollapsed()"
        />
      </div>
    </template>
    <template #content-header>
      <UBreadcrumb class="m-5" :items="breadcrumb">
        <template #dropdown="{ item }">
          <UDropdownMenu :items="item.children">
            <UButton
              :icon="item.icon"
              :avatar="item.avatar"
              :label="item.label"
              color="neutral"
              variant="link"
              class="p-0.5"
            />
          </UDropdownMenu>
        </template>
      </UBreadcrumb>
    </template>
    <slot />
  </Panel>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import type { Project } from "~/types/models";
import { targetTypes } from "~/constants";

const api = useApi();
const route = useRoute();
const userStore = useUserStore();
const breadcrumb = ref([]);
const items = ref([]);
const projectEntity = ref({ name: "Rekono" });
const mounting = ref(false);
const allProjects = ref<Project[]>([]);

function onProjectChange() {
  console.log("onProjectChange");
  if (!route.params.project_id) {
    projectEntity.value = { name: "Rekono" };
    return;
  }
  breadcrumb.value = [
    {
      label: "Home",
      icon: "i-lucide-house",
      to: "/",
    },
    {
      label: "Projects",
      icon: "i-lucide-folder",
      to: "/projects/",
    },
  ];
  api.get(`/api/projects/${route.params.project_id}/`).then((project) => {
    projectEntity.value = project;
    if (allProjects.value.length === 0) {
      api.list("/api/projects/", {}, true).then((response) => {
        allProjects.value = response.items;
        getProjectBreadcrum(project);
      });
    } else {
      getProjectBreadcrum(project);
    }
  });
  items.value = [
    {
      label: "Details",
      icon: "i-lucide-folder",
      to: `/projects/${route.params.project_id}`,
    },
    {
      label: "Targets",
      icon: "i-lucide-locate-fixed",
      to: `/projects/${route.params.project_id}/targets`,
    },
    {
      label: "Scans",
      icon: "i-lucide-play",
      to: `/projects/${route.params.project_id}/scans`,
    },
    {
      label: "Assets",
      icon: "i-lucide-server",
      defaultOpen: true,
      children: [
        {
          label: "Hosts",
          icon: "i-lucide-server",
          to: `/projects/${route.params.project_id}/hosts`,
        },
        {
          label: "Ports",
          icon: "i-lucide-ethernet-port",
          to: `/projects/${route.params.project_id}/ports`,
        },
        {
          label: "Technologies",
          icon: "i-lucide-layers",
          to: `/projects/${route.params.project_id}/technologies`,
        },
        {
          label: "Paths",
          icon: "i-lucide-slash",
          to: `/projects/${route.params.project_id}/paths`,
        },
      ],
    },
    {
      label: "Findings",
      icon: "i-lucide-scan",
      defaultOpen: true,
      children: [
        {
          label: "OSINT",
          icon: "i-lucide-rss",
          to: `/projects/${route.params.project_id}/osint`,
        },
        {
          label: "Credentials",
          icon: "i-lucide-key",
          to: `/projects/${route.params.project_id}/credentials`,
        },
        {
          label: "Vulnerabilities",
          icon: "i-lucide-bug",
          to: `/projects/${route.params.project_id}/vulnerabilities`,
        },
        {
          label: "Exploits",
          icon: "i-lucide-flame",
          to: `/projects/${route.params.project_id}/exploits`,
        },
      ],
    },
    {
      label: "Metrics",
      icon: "i-lucide-chart-bar",
      to: `/projects/${route.params.project_id}/metrics`,
    },
    {
      label: "Reports",
      icon: "i-lucide-file-text",
      to: `/projects/${route.params.project_id}/reports`,
    },

    {
      label: "Notes",
      icon: "i-lucide-notebook",
      to: `/projects/${route.params.project_id}/notes`,
    },
    {
      label: "Alerts",
      icon: "i-lucide-triangle-alert",
      to: `/projects/${route.params.project_id}/alerts`,
    },
  ];
  if (userStore.is_admin) {
    items.value.push({
      label: "Members",
      icon: "i-lucide-users",
      to: `/projects/${route.params.project_id}/members`,
    });
  }
  api
    .list("hosts/", { project: route.params.project_id }, false, 1, 1)
    .then((response: object) => {
      if (items.value[3]?.children?.[0]) {
        items.value[3].children[0].badge = response.total.toString();
      }
    });
  api
    .list("ports/", { project: route.params.project_id }, false, 1, 1)
    .then((response: object) => {
      if (items.value[3]?.children?.[1]) {
        items.value[3].children[1].badge = response.total.toString();
      }
    });
  api
    .list("technologies/", { project: route.params.project_id }, false, 1, 1)
    .then((response: object) => {
      if (items.value[3]?.children?.[2]) {
        items.value[3].children[2].badge = response.total.toString();
      }
    });
  api
    .list("paths/", { project: route.params.project_id }, false, 1, 1)
    .then((response: object) => {
      if (items.value[3]?.children?.[3]) {
        items.value[3].children[3].badge = response.total.toString();
      }
    });
  api
    .list("osint/", { project: route.params.project_id }, false, 1, 1)
    .then((response: object) => {
      if (items.value[4]?.children?.[0]) {
        items.value[4].children[0].badge = response.total.toString();
      }
    });
  api
    .list("credentials/", { project: route.params.project_id }, false, 1, 1)
    .then((response: object) => {
      if (items.value[4]?.children?.[1]) {
        items.value[4].children[1].badge = response.total.toString();
      }
    });
  api
    .list("vulnerabilities/", { project: route.params.project_id }, false, 1, 1)
    .then((response: object) => {
      if (items.value[4]?.children?.[2]) {
        items.value[4].children[2].badge = response.total.toString();
      }
    });
  api
    .list("exploits/", { project: route.params.project_id }, false, 1, 1)
    .then((response: object) => {
      if (items.value[4]?.children?.[3]) {
        items.value[4].children[3].badge = response.total.toString();
      }
    });
}

function getProjectBreadcrum(project: Project) {
  const children: NavigationItem[] = [];
  for (const projectOption of allProjects.value) {
    if (projectOption.id !== project.id) {
      children.push({
        label: projectOption.name,
        avatar: { text: projectOption.name.charAt(0).toUpperCase() },
        to: `/projects/${projectOption.id}`,
      });
    }
  }
  breadcrumb.value.push({
    slot: children.length > 0 ? "dropdown" : undefined,
    label: project.name,
    avatar: { text: project.name.charAt(0).toUpperCase() },
    to: `/projects/${project.id}`,
    children: children,
  });
  if (mounting.value) {
    if (route.params.target_id) onTargetChange();
    if (route.params.scan_id) onScanChange();
    if (route.params.note_id) onNoteChange();
  }
  mounting.value = false;
}

function cleanSecondaryLinks(
  entityId: number,
  entitiesLink: Record<string, string>,
): boolean {
  if (breadcrumb.value.length > 3) {
    breadcrumb.value = breadcrumb.value.slice(0, 3);
  }
  if (!entityId) {
    return false;
  } else {
    breadcrumb.value.push(entitiesLink);
    return true;
  }
}

function onTargetChange() {
  const conclusion = cleanSecondaryLinks(route.params.target_id, {
    label: "Targets",
    icon: "i-lucide-locate-fixed",
    to: `/projects/${route.params.project_id}/targets`,
  });
  if (!conclusion) return;
  api
    .list("/api/targets/", { project: route.params.project_id }, true)
    .then((response) => {
      let currentTarget = null;
      const children: NavigationItem[] = [];
      for (const targetOption of response.items) {
        if (targetOption.id !== parseInt(route.params.target_id)) {
          children.push({
            label: targetOption.target,
            icon: targetTypes.find((t) => t.value === targetOption.type)?.icon,
            to: `/projects/${route.params.project_id}/targets/${targetOption.id}`,
          });
        } else {
          currentTarget = targetOption;
        }
      }
      if (currentTarget) {
        breadcrumb.value.push({
          slot: children.length > 0 ? "dropdown" : undefined,
          label: currentTarget.target,
          icon: targetTypes.find((t) => t.value === currentTarget.type)?.icon,
          to: `/projects/${route.params.project_id}/targets/${route.params.target_id}`,
          children: children,
        });
      }
    });
}

function onScanChange() {
  cleanSecondaryLinks(route.params.scan_id, {
    label: "Scans",
    icon: "i-lucide-play",
    to: `/projects/${route.params.project_id}/scans`,
  });
}

function onNoteChange() {
  cleanSecondaryLinks(route.params.note_id, {
    label: "Notes",
    icon: "i-lucide-notebook",
    to: `/projects/${route.params.project_id}/notes`,
  });
}

watch(() => route.params.project_id, onProjectChange);
watch(() => route.params.target_id, onTargetChange);
watch(() => route.params.scan_id, onScanChange);
watch(() => route.params.note_id, onNoteChange);

onMounted(() => {
  mounting.value = true;
  onProjectChange();
});
</script>
