<template>
  <CrudPage :config="config">
    <template #item="{ item, onDelete }">
      <User :user="item">
        <div v-if="item.id !== userStore.user" class="flex justify-end">
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
import { roles } from "~/constants";

const userStore = useUserStore();
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
      options: roles.map((role) => {
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
  deleteMessage: (user: User) =>
    buildDeleteMessage(
      "project member",
      getUserDisplayName(user),
      undefined,
      "The user will lose access to the project and its resources immediately",
    ),
  deleteEndpoint: (user: User) =>
    `/api/projects/${route.params.project_id}/members/${user.id}/`,
  canRead: userStore.is_admin,
  canCreate: userStore.is_admin,
  canEdit: false,
  canDelete: userStore.is_admin,
});
</script>
