<template>
  <CrudPage ref="page" :config="config">
    <template #item="{ item, onEdit, onDelete }">
      <UPageCard
        :title="utils.firstUpper(utils.smartLowerCase(item.item))"
        :description="
          item.value && item.item !== 'Trending CVE' ? item.value : undefined
        "
        variant="subtle"
        spotlight
        class="relative"
      >
        <template #leading>
          <UIcon
            :name="
              backend.alerts.find((alert) => alert.item === item.item)?.icon
            "
            :class="`text-2xl ${item.enabled ? 'text-success' : 'text-primary'}`"
          />
        </template>
        <UTooltip
          :text="item.subscribed ? 'Unsubscribe' : 'Subscribe'"
          class="absolute top-4 right-4"
        >
          <UButton
            variant="subtle"
            :color="item.subscribed ? 'primary' : 'neutral'"
            @click="toggleSubscription(item)"
          >
            <UIcon
              :name="item.subscribed ? 'i-lucide-bell-ring' : 'i-lucide-bell'"
              :class="item.subscribed ? 'fill-current' : ''"
            />
            <span>{{ item.subscribers.length }}</span>
          </UButton>
        </UTooltip>
        <UDropdownMenu
          v-if="getActions(item, onEdit, onDelete).length > 0"
          :items="getActions(item, onEdit, onDelete)"
          class="absolute bottom-4 right-4"
        >
          <UButton
            icon="i-lucide-more-horizontal"
            variant="ghost"
            color="neutral"
          />
        </UDropdownMenu>
      </UPageCard>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import type { Alert } from "~/types/models";
import { useUserStore } from "~/store/user";

const userStore = useUserStore();
const api = useApi("/api/alerts/");
const backend = useBackend();
const utils = useUtils();
const route = useRoute();
const ownerOptions = ref([]);
const page = ref();

const config: CrudConfig<Alert> = reactive({
  endpoint: "/api/alerts/",
  entityName: "Alert",
  entityNamePlural: "Alerts",
  icon: "i-lucide-triangle-alert",
  useGrid: true,
  searchable: true,
  searchPlaceholder: "Search alerts...",
  filters: [
    {
      key: "enabled",
      label: "Enabled",
      type: "checkbox" as const,
    },
    {
      key: "owner",
      label: "Owner",
      icon: "i-lucide-user",
      type: "select" as const,
      options: () => Promise.resolve(ownerOptions.value),
    },
  ],
  defaultFilters: { project: route.params.project_id },
  ordering: [
    "id",
    { id: "project", label: "Project" },
    { id: "item", label: "Item" },
    { id: "owner", label: "Owner" },
  ],
  defaultOrdering: "-id",
  pageSize: 24,
  pageSizeOptions: [24, 50, 100],
  defaultBody: { project: route.params.project_id },
  createForm: resolveComponent("FormAlert"),
  editForm: resolveComponent("FormAlert"),
  deleteMessage: (alert: Alert) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this alert?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: alert.item,
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
  ],
  canRead: true,
  canCreate: true,
  canEdit: canEdit,
  canDelete: canDelete,
});

onMounted(() => {
  backend.getUserOptions(ownerOptions);
});

function canEdit(alert: Alert): boolean {
  const field = backend.alerts.find(
    (definition) => definition.item == alert.item,
  )?.field;
  return (
    field &&
    field !== "trending" &&
    (userStore.is_admin || alert.owner?.id === parseInt(userStore.user))
  );
}

function canDelete(alert: Alert): boolean {
  return userStore.is_admin || alert.owner?.id === parseInt(userStore.user);
}

function getActions(item: Alert, onEdit: () => void, onDelete: () => void) {
  const actions = [];
  if (canEdit(item)) {
    actions.push({
      label: "Edit",
      icon: "i-lucide-edit",
      onSelect: onEdit,
    });
  }
  if (item.enabled) {
    actions.push({
      label: "Disable",
      icon: "i-lucide-x-circle",
      color: "warning",
      onSelect: () => toggleEnable(item),
    });
  } else {
    actions.push({
      label: "Enable",
      icon: "i-lucide-check-circle",
      color: "success",
      onSelect: () => toggleEnable(item),
    });
  }
  if (canDelete(item)) {
    actions.push({
      label: "Delete",
      icon: "i-lucide-trash",
      color: "error",
      onSelect: onDelete,
    });
  }
  return actions;
}

function toggleEnable(alert: Alert) {
  const method = alert.enabled ? api.remove : api.create;
  method(`${alert.id}/enable/`, {}).then(() => {
    page.value.fetch();
  });
}

function toggleSubscription(alert: Alert) {
  const method = alert.subscribed ? api.remove : api.create;
  method(`${alert.id}/subscription/`, {}).then(() => {
    alert.subscribed = !alert.subscribed;
    if (alert.subscribed) {
      alert.subscribers.push(userStore.user);
    } else {
      alert.subscribers.splice(alert.subscribers.indexOf(userStore.user));
    }
  });
}
</script>
