<template>
  <CrudPage :config="config">
    <template #item="{ item, onEdit, onDelete }">
      <User :user="item">
        <div class="flex items-center justify-between">
          <div class="flex1">
            <UBadge
              v-if="item.is_active === true"
              icon="i-lucide-check-circle"
              label="Active"
              color="success"
              variant="subtle"
            />
            <UBadge
              v-else-if="item.is_active === false"
              icon="i-lucide-x-circle"
              label="Disabled"
              color="error"
              variant="subtle"
            />
            <UBadge
              v-else
              icon="i-lucide-clock"
              label="Pending"
              color="warning"
              variant="subtle"
            />
          </div>
          <div class="flex1">
            <UDropdownMenu
              v-if="item.id.toString() !== userStore.user"
              :items="getUserActions(item, onEdit, onDelete)"
            >
              <UButton
                icon="i-lucide-more-horizontal"
                variant="ghost"
                color="neutral"
              />
            </UDropdownMenu>
          </div>
        </div>
      </User>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import type { User } from "~/types/models";
import { useUserStore } from "~/store/user";
import * as z from "zod";
import { roles } from "~/constants";

const userStore = useUserStore();
const validation = useValidation();
const toast = useToast();
const api = useApi("/api/users/");
const roleOptions = roles.map((role) => {
  return { label: role, value: role };
});

function getUserActions(item: User, onEdit: () => void, onDelete: () => void) {
  const actions = [];
  if (item.is_active === false) {
    actions.push({
      label: "Enable",
      icon: "i-lucide-check-circle",
      onSelect: () => {
        api.create(`${item.id}/enable/`, {}).then(() => {
          toast.add({
            title: "User enabled",
            description: `${getUserDisplayName(item)} has been enabled successfully`,
            color: "success",
          });
          item.is_active = true;
        });
      },
    });
  }
  if (item.is_active === null || item.is_active === undefined) {
    actions.push({
      label: "Resend invitation",
      icon: "i-lucide-mail",
      onSelect: () => {
        api.create(`${item.id}/resend/`, {}).then(() => {
          toast.add({
            title: "Invitation sent",
            description: `Invitation has been resent to ${getUserDisplayName(item)}`,
            color: "success",
          });
        });
      },
    });
  }
  return [
    ...actions,
    ...[
      {
        label: "Copy email",
        icon: "i-lucide-copy",
        onSelect: () => {
          navigator.clipboard.writeText(String(item.email));
          toast.add({
            title: "User email copied to clipboard",
            color: "success",
          });
        },
      },
      {
        label: "Edit",
        icon: "i-lucide-edit",
        onSelect: onEdit,
      },
      {
        label: "Disable",
        icon: "i-lucide-x-circle",
        color: "error",
        onSelect: onDelete,
      },
    ],
  ];
}

const config: CrudConfig<User> = reactive({
  endpoint: "/api/users/",
  entityName: "User",
  entityNamePlural: "Users",
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
      options: roleOptions,
    },
    {
      key: "is_active",
      label: "Active",
      type: "checkbox",
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
  defaultOrdering: "-id",
  pageSize: 24,
  pageSizeOptions: [24, 50, 100],
  createFormFields: [
    {
      key: "email",
      label: "Email",
      type: "text",
      required: true,
      placeholder: "user@example.com",
      icon: "i-lucide-mail",
    },
    {
      key: "role",
      label: "Role",
      type: "select",
      required: true,
      options: roleOptions,
      icon: "i-lucide-shield",
      placeholder: "Select the user role",
    },
  ],
  createFormSchema: z.object({
    email: validation.email(),
    role: z.enum(roles),
  }),
  editFormFields: [
    {
      key: "role",
      label: "Role",
      type: "select",
      required: true,
      options: roleOptions,
      icon: "i-lucide-shield",
    },
  ],
  editFormSchema: z.object({
    role: z.enum(roles),
  }),
  modalAvatar: (user: User) => ({
    text: getUserDisplayName(user).charAt(0).toUpperCase(),
  }),
  deleteMessage: (user: User) =>
    buildDeleteMessage(
      "user",
      getUserDisplayName(user),
      undefined,
      undefined,
      "disable",
    ),
  deleteVerb: "Disable",
  canRead: userStore.is_admin,
  canCreate: userStore.is_admin,
  canEdit: userStore.is_admin,
  canDelete: userStore.is_admin,
});
</script>
