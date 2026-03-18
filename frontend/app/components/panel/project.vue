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

const api = useApi();
const route = useRoute();
const userStore = useUserStore();
const backend = useBackend();
const breadcrumb = ref([]);
const items = ref([]);
const projectEntity = ref({ name: "Rekono" });
const currentTask = useState<Task | null>("currentTask", () => null);
const allProjects = ref<Project[]>([]);

function onProjectChange() {
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
      to: `/projects/${route.params.project_id}/assets`,
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
      if (items.value[3]) {
        items.value[3].badge = response.total.toString();
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
  if (route.params.target_id) {
    onTargetChange();
  }
  if (route.params.scan_id) {
    onScanChange();
  }
}

function onTargetChange() {
  if (!route.params.target_id) {
    if (breadcrumb.value.length > 3) {
      breadcrumb.value = breadcrumb.value.slice(0, 3);
    }
    return;
  }
  if (breadcrumb.value.length > 3) {
    breadcrumb.value = breadcrumb.value.slice(0, 4);
  } else {
    breadcrumb.value.push({
      label: "Targets",
      icon: "i-lucide-locate-fixed",
      to: `/projects/${route.params.project_id}/targets`,
    });
  }
  api
    .list("/api/targets/", { project: route.params.project_id }, true)
    .then((response) => {
      let currentTarget = null;
      const children: NavigationItem[] = [];
      for (const targetOption of response.items) {
        if (targetOption.id !== parseInt(route.params.target_id)) {
          children.push({
            label: targetOption.target,
            icon: backend.targetTypes.find((t) => t.value === targetOption.type)
              ?.icon,
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
          icon: backend.targetTypes.find((t) => t.value === currentTarget.type)
            ?.icon,
          to: `/projects/${route.params.project_id}/targets/${route.params.target_id}`,
          children: children,
        });
      }
    });
}

function onScanChange() {
  if (!route.params.scan_id) {
    if (breadcrumb.value.length > 3) {
      breadcrumb.value = breadcrumb.value.slice(0, 3);
    }
    return;
  }
  if (breadcrumb.value.length > 3) {
    breadcrumb.value = breadcrumb.value.slice(0, 4);
  } else {
    breadcrumb.value.push({
      label: "Scans",
      icon: "i-lucide-play",
      to: `/projects/${route.params.project_id}/scans`,
    });
  }
  breadcrumb.value.push({
    label: currentTask.value?.process
      ? currentTask.value.process.name
      : currentTask.value?.configuration?.tool?.name,
    icon: currentTask.value.process
      ? "i-lucide-workflow"
      : currentTask.value.configuration?.tool?.icon
        ? undefined
        : "i-lucide-square-terminal",
    avatar: currentTask.value.configuration?.tool?.icon
      ? { src: currentTask.value.configuration?.tool?.icon }
      : undefined,
    to: `/projects/${route.params.project_id}/scans/${route.params.scan_id}`,
  });
}

watch(
  () => route.params.project_id,
  () => {
    onProjectChange();
  },
);

watch(
  () => route.params.target_id,
  () => {
    onTargetChange();
  },
);

watch(
  () => route.params.scan_id,
  () => {
    onScanChange();
  },
);

onMounted(() => {
  onProjectChange();
});
</script>
