<template>
  <Panel :navigation-items="items" storage-key="panel">
    <template #panel-header="{ open }">
      <div
        v-if="currentProject"
        class="flex items-center w-full justify-start gap-2"
      >
        <UAvatar
          :text="currentProject.name.charAt(0).toUpperCase()"
          class="bg-primary-500"
          :ui="{ fallback: 'text-white' }"
          :alt="currentProject.name"
          width="30"
        />
        <h1 v-if="open" class="text-2xl font-bold font-mono">
          {{ currentProject.name }}
        </h1>
      </div>
    </template>
    <template #content-header>
      <UBreadcrumb class="mt-5 ml-5" :items="responsiveBreadcrum">
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
import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";
import { useUserStore } from "~/store/user";
import type { Project } from "~/types/models";
import { targetTypes } from "~/constants";

const api = useApi();
const route = useRoute();
const userStore = useUserStore();
const { panelRefresh, projectHasActiveFindings } = usePanel();
const { currentProject, setCurrentProject } = useCurrentProject();
const breakpoints = useBreakpoints(breakpointsTailwind);
const breadcrumb = ref([]);
const responsiveBreadcrum = computed(() =>
  breakpoints.smaller("sm").value && breadcrumb.value.length > 3
    ? [
        breadcrumb.value[0],
        {
          slot: "dropdown" as const,
          icon: "i-lucide-ellipsis",
          children: breadcrumb.value.slice(1, -1),
        },
        breadcrumb.value[breadcrumb.value.length - 1],
      ]
    : breadcrumb.value,
);
const mounting = ref(false);
const allProjects = ref<Project[]>([]);
const projectBadges = reactive({
  hosts: "",
  ports: "",
  technologies: "",
  paths: "",
  osint: "",
  credentials: "",
  vulnerabilities: "",
  exploits: "",
});
const items = computed(() => [
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
        badge: projectBadges.hosts || undefined,
      },
      {
        label: "Ports",
        icon: "i-lucide-ethernet-port",
        to: `/projects/${route.params.project_id}/ports`,
        badge: projectBadges.ports || undefined,
      },
      {
        label: "Technologies",
        icon: "i-lucide-layers",
        to: `/projects/${route.params.project_id}/technologies`,
        badge: projectBadges.technologies || undefined,
      },
      {
        label: "Paths",
        icon: "i-lucide-slash",
        to: `/projects/${route.params.project_id}/paths`,
        badge: projectBadges.paths || undefined,
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
        badge: projectBadges.osint || undefined,
      },
      {
        label: "Credentials",
        icon: "i-lucide-key",
        to: `/projects/${route.params.project_id}/credentials`,
        badge: projectBadges.credentials || undefined,
      },
      {
        label: "Vulnerabilities",
        icon: "i-lucide-bug",
        to: `/projects/${route.params.project_id}/vulnerabilities`,
        badge: projectBadges.vulnerabilities || undefined,
      },
      {
        label: "Exploits",
        icon: "i-lucide-flame",
        to: `/projects/${route.params.project_id}/exploits`,
        badge: projectBadges.exploits || undefined,
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
  ...(userStore.is_admin
    ? [
        {
          label: "Members",
          icon: "i-lucide-users",
          to: `/projects/${route.params.project_id}/members`,
        },
      ]
    : []),
]);

function onProjectChange() {
  if (!route.params.project_id) {
    setCurrentProject(null);
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
  Object.keys(projectBadges).forEach((key) => (projectBadges[key] = ""));
  projectHasActiveFindings.value = false;
  api.get(`/api/projects/${route.params.project_id}/`).then((data) => {
    setCurrentProject(data);
    if (allProjects.value.length === 0) {
      api.list("/api/projects/", {}, true).then((response) => {
        allProjects.value = response.items;
        getProjectBreadcrum(data);
      });
    } else {
      getProjectBreadcrum(data);
    }
  });
  loadProjectBadges();
}

function loadProjectBadges() {
  if (!route.params.project_id) return;
  const openFindings = { project: route.params.project_id, is_fixed: false };
  const activeFindings = {
    project: route.params.project_id,
    triage_status__in: "True Positive,Untriaged",
    is_fixed: false,
  };
  Promise.all([
    api
      .list("hosts/", openFindings, false, 1, 1)
      .then(
        (response: object) =>
          (projectBadges.hosts = formatCount(response.total)),
      ),
    api
      .list("ports/", openFindings, false, 1, 1)
      .then(
        (response: object) =>
          (projectBadges.ports = formatCount(response.total)),
      ),
    api
      .list("technologies/", openFindings, false, 1, 1)
      .then(
        (response: object) =>
          (projectBadges.technologies = formatCount(response.total)),
      ),
    api
      .list("paths/", openFindings, false, 1, 1)
      .then(
        (response: object) =>
          (projectBadges.paths = formatCount(response.total)),
      ),
    api
      .list("osint/", activeFindings, false, 1, 1)
      .then(
        (response: object) =>
          (projectBadges.osint = formatCount(response.total)),
      ),
    api
      .list("credentials/", activeFindings, false, 1, 1)
      .then(
        (response: object) =>
          (projectBadges.credentials = formatCount(response.total)),
      ),
    api
      .list("vulnerabilities/", activeFindings, false, 1, 1)
      .then(
        (response: object) =>
          (projectBadges.vulnerabilities = formatCount(response.total)),
      ),
    api
      .list("exploits/", activeFindings, false, 1, 1)
      .then(
        (response: object) =>
          (projectBadges.exploits = formatCount(response.total)),
      ),
  ]).finally(
    () =>
      (projectHasActiveFindings.value = Object.values(projectBadges).some(
        (value) => !["", "0"].includes(value),
      )),
  );
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
    if (route.params.osint_id) onOsintChange();
    if (route.params.host_id) onHostChange();
    if (route.params.port_id) onPortChange();
    if (route.params.path_id) onPathChange();
    if (route.params.credential_id) onCredentialChange();
    if (route.params.technology_id) onTechnologyChange();
    if (route.params.vulnerability_id) onVulnerabilityChange();
    if (route.params.exploit_id) onExploitChange();
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
  if (!route.params.project_id || !entityId) {
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

function onOsintChange() {
  cleanSecondaryLinks(route.params.osint_id, {
    label: "OSINT",
    icon: "i-lucide-rss",
    to: `/projects/${route.params.project_id}/osint`,
  });
}

function onHostChange() {
  cleanSecondaryLinks(route.params.host_id, {
    label: "Hosts",
    icon: "i-lucide-server",
    to: `/projects/${route.params.project_id}/hosts`,
  });
}

function onPortChange() {
  cleanSecondaryLinks(route.params.port_id, {
    label: "Ports",
    icon: "i-lucide-ethernet-port",
    to: `/projects/${route.params.project_id}/ports`,
  });
}

function onPathChange() {
  cleanSecondaryLinks(route.params.path_id, {
    label: "Paths",
    icon: "i-lucide-slash",
    to: `/projects/${route.params.project_id}/paths`,
  });
}

function onCredentialChange() {
  cleanSecondaryLinks(route.params.credential_id, {
    label: "Credentials",
    icon: "i-lucide-key",
    to: `/projects/${route.params.project_id}/credentials`,
  });
}

function onTechnologyChange() {
  cleanSecondaryLinks(route.params.technology_id, {
    label: "Technologies",
    icon: "i-lucide-layers",
    to: `/projects/${route.params.project_id}/technologies`,
  });
}

function onVulnerabilityChange() {
  cleanSecondaryLinks(route.params.vulnerability_id, {
    label: "Vulnerabilities",
    icon: "i-lucide-bug",
    to: `/projects/${route.params.project_id}/vulnerabilities`,
  });
}

function onExploitChange() {
  cleanSecondaryLinks(route.params.exploit_id, {
    label: "Exploits",
    icon: "i-lucide-flame",
    to: `/projects/${route.params.project_id}/exploits`,
  });
}

watch(panelRefresh, loadProjectBadges);
watch(() => route.params.project_id, onProjectChange);
watch(
  () => currentProject.value?.name,
  (name) => {
    if (!name || breadcrumb.value.length < 3) return;
    const item = breadcrumb.value[2];
    item.label = name;
    item.avatar = { text: name.charAt(0).toUpperCase() };
    const cached = allProjects.value.find(
      (p) => p.id === currentProject.value?.id,
    );
    if (cached) cached.name = name;
  },
);
watch(() => route.params.target_id, onTargetChange);
watch(() => route.params.scan_id, onScanChange);
watch(() => route.params.note_id, onNoteChange);
watch(() => route.params.osint_id, onOsintChange);
watch(() => route.params.host_id, onHostChange);
watch(() => route.params.port_id, onPortChange);
watch(() => route.params.path_id, onPathChange);
watch(() => route.params.credential_id, onCredentialChange);
watch(() => route.params.technology_id, onTechnologyChange);
watch(() => route.params.vulnerability_id, onVulnerabilityChange);
watch(() => route.params.exploit_id, onExploitChange);

onMounted(() => {
  mounting.value = true;
  onProjectChange();
});
</script>
