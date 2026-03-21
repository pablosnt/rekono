<template>
  <CrudPage :config="config">
    <template #item="{ item, onDelete }">
      <User :user="item">
        <div
          v-if="item.id.toString() !== userStore.user"
          class="flex justify-end"
        >
          <UTooltip
            text="Delete member"
            :content="{ side: 'left', sideOffset: 8, collisionPadding: 8 }"
          >
            <UButton
              icon="i-lucide-x"
              variant="subtle"
              class="justify-end"
              @click="onDelete"
            />
          </UTooltip>
        </div>
      </User>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import type { User } from "~/types/models";
import { useUserStore } from "~/store/user";

definePageMeta({ layout: "project" });
const userStore = useUserStore();
const backend = useBackend();
const route = useRoute();

const config: CrudConfig<User> = reactive({
  endpoint: "/api/users/",
  entityName: "Member",
  entityNamePlural: "Members",
  icon: "i-lucide-users",
  useGrid: true,
  searchable: true,
  searchPlaceholder: "Search users...",
  filters: [
    {
      key: "role",
      label: "Role",
      icon: "i-lucide-shield",
      type: "select" as const,
      options: backend.roles.map((role) => {
        return { label: role, value: role };
      }),
    },
  ],
  ordering: [
    "id",
    { id: "username", label: "Username" },
    { id: "first_name", label: "First Name" },
    { id: "last_name", label: "Last Name" },
    "email",
    { id: "date_joined", label: "Date Joined" },
    { id: "last_login", label: "Last Login" },
  ],
  defaultFilters: { project: route.params.project_id },
  defaultOrdering: "-id",
  pageSize: 24,
  pageSizeOptions: [24, 50, 100],
  createForm: resolveComponent("ProjectsMembersForm"),
  createLabel: "Add",
  deleteMessage: (user: User) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this project member?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: backend.getUserDisplayName(user),
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "warning",
        icon: "i-lucide-triangle-alert",
        description:
          "The user will lose access to the project and its resources immediately",
        class: "mt-4",
      },
    },
  ],
  deleteEndpoint: (user: User) =>
    `/api/projects/${route.params.project_id}/members/${user.id}/`,
  canRead: userStore.is_admin,
  canCreate: userStore.is_admin,
  canEdit: false,
  canDelete: userStore.is_admin,
});
</script>
