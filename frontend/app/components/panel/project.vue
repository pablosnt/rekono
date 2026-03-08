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
    <slot :project="projectEntity" />
  </Panel>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const api = useApi();
const route = useRoute();
const userStore = useUserStore();
const breadcrumb = ref([]);
const items = ref([]);
const projectEntity = ref();

const update = () => {
  if (!route.params.project_id) {
    projectEntity.value = {name: 'Rekono'};
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
    api.get("stats/top-projects/").then((top_projects: object) => {
      const children: NavigationItem[] = [];
      for (let i = 0; i < top_projects.length; i++) {
        if (top_projects[i].id === project.id) {
          continue;
        }
        children.push({
          label: top_projects[i].name,
          avatar: { text: top_projects[i].name.charAt(0).toUpperCase() },
          to: `/projects/${top_projects[i].id}`,
        });
      }
      breadcrumb.value.push({
        slot: "dropdown",
        label: project.name,
        avatar: { text: project.name.charAt(0).toUpperCase() },
        to: `/projects/${project.id}`,
        children: children,
      });
    });
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
          icon: "i-lucide-globe",
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
};

watch(
  () => route.params.project_id,
  () => {
    update();
  },
);

onMounted(() => {
  update();
});
</script>
