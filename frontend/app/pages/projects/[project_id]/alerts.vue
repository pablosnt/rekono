<template>
  <CrudPage ref="page" :config="config">
    <template #item="{ item, onEdit, onDelete }">
      <UPageCard
        :title="firstUpper(smartLowerCase(item.item))"
        :description="
          item.value && item.item !== 'Trending CVE' ? item.value : undefined
        "
        variant="subtle"
        spotlight
        class="relative"
      >
        <template #leading>
          <UIcon
            :name="alertItems.find((alert) => alert.item === item.item)?.icon"
            :class="[
              'text-2xl',
              item.enabled ? 'text-success' : 'text-primary',
            ]"
          />
        </template>
        <UTooltip
          :text="item.subscribed ? 'Unsubscribe' : 'Subscribe'"
          class="absolute top-4 right-4"
          :content="{ side: 'left', sideOffset: 8, collisionPadding: 8 }"
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
            <span>{{ formatCount(item.subscribers.length) }}</span>
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
import { alertItems } from "~/constants";

const userStore = useUserStore();
const api = useApi("/api/alerts/");
const options = useOptions();
const route = useRoute();
const userOptions = ref([]);
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
      options: userOptions,
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
  createForm: resolveComponent("AlertsForm"),
  editForm: resolveComponent("AlertsForm"),
  deleteMessage: (alert: Alert) => buildDeleteMessage("alert", alert.item),
  canRead: true,
  canCreate: true,
  canEdit: canEdit,
  canDelete: canDelete,
});

onMounted(() => {
  options.users(userOptions, { is_active: true });
});

function canEdit(alert: Alert): boolean {
  const field = alertItems.find(
    (definition) => definition.item == alert.item,
  )?.field;
  return (
    field &&
    field !== "trending" &&
    (userStore.is_admin || alert.owner?.id === userStore.user)
  );
}

function canDelete(alert: Alert): boolean {
  return userStore.is_admin || alert.owner?.id === userStore.user;
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
