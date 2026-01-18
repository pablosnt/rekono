<template>
  <CrudPage :config="config">
    <template #item="{ item, onEdit, onDelete }">
      <UPageCard variant="subtle" spotlight>
        <template #leading>
          <div class="flex justify-end gap-2 items-start">
            <UUser
              class="w-76"
              :name="utils.truncateText(utils.getUserDisplayName(item), 28)"
              :description="item.role"
              :avatar="{
                text: utils.getUserDisplayName(item).charAt(0).toUpperCase(),
                class:
                  item.id.toString() === userStore.user
                    ? 'bg-primary-500 text-white'
                    : '',
              }"
              size="xl"
            />
            <UTooltip
              v-if="item.is_active && (item.last_login || item.date_joined)"
              class="w-8"
            >
              <UButton icon="i-lucide-clock" color="neutral" variant="ghost" />
              <template #content>
                <div>
                  <p v-if="item.last_login">
                    Last login
                    {{
                      utils
                        .formatRelativeDatetime(item.last_login)
                        .toLowerCase()
                    }}
                  </p>
                  <p v-if="item.date_joined">
                    Joined
                    {{
                      utils
                        .formatRelativeDatetime(item.date_joined)
                        .toLowerCase()
                    }}
                  </p>
                </div>
              </template>
            </UTooltip>
          </div>
        </template>
        <div class="flex items-center justify-between mt-4">
          <div class="flex items-center gap-2">
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
          <UDropdownMenu
            v-if="item.id.toString() !== userStore.user"
            :items="getUserActions(item, onEdit, onDelete)"
            :content="{ align: 'end' }"
          >
            <UButton
              icon="i-lucide-more-horizontal"
              variant="ghost"
              color="gray"
            />
          </UDropdownMenu>
        </div>
      </UPageCard>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import { h } from "vue";
import type { CrudConfig } from "~/types/crud";
import type { User } from "~/types/users";
import { useUserStore } from "~/store/user";
import * as z from "zod";

const userStore = useUserStore();
const utils = useUtils();
const toast = useToast();
const api = useApi("/api/users/");

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
            description: `${utils.getUserDisplayName(item)} has been enabled successfully`,
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
            description: `Invitation has been resent to ${utils.getUserDisplayName(item)}`,
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
      options: utils.roleOptions,
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
  pageSizeOptions: [24, 48, 96],
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
      options: utils.roleOptions,
      icon: "i-lucide-shield",
      placeholder: "Select the user role",
    },
  ],
  createFormSchema: z.object({
    email: z.email(),
    role: z.enum(
      utils.roleOptions.map((t) => t.value) as [string, ...string[]],
    ),
  }),
  updateOnCreateModalOpen: true,
  editFormFields: [
    {
      key: "role",
      label: "Role",
      type: "select",
      required: true,
      options: utils.roleOptions,
      icon: "i-lucide-shield",
    },
  ],
  editFormSchema: z.object({
    role: z.enum(
      utils.roleOptions.map((t) => t.value) as [string, ...string[]],
    ),
  }),
  updateOnEditModalOpen: true,
  modalAvatar: (user: User) => ({
    text: utils.getUserDisplayName(user).charAt(0).toUpperCase(),
  }),
  deleteMessage: (user: User) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to disable this user?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: utils.getUserDisplayName(user),
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
  ],
  deleteVerb: "Disable",
  canRead: userStore.is_admin,
  canCreate: userStore.is_admin,
  canEdit: userStore.is_admin,
  canDelete: userStore.is_admin,
});
</script>
