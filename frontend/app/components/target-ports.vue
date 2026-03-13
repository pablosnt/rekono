<template>
  <div>
    <CrudPage ref="page" :config="config" />
    <CrudDeleteModal
      :open="deleteAuthenticationOpen"
      :item="selectedTargetPort?.authentication"
      :config="{
        entityName: 'Authentication',
        deleteMessage: (authentication: Authentication) => [
          {
            component: h(
              'p',
              { class: 'text-gray-900 dark:text-white font-medium' },
              `Are you sure you want to delete the authentication ${authentication.name} for the target port ${selectedTargetPort.port}?`,
            ),
          },
        ],
      }"
      :api="authenticationApi"
      @open="(open) => (deleteAuthenticationOpen = open)"
      @deleted="page.fetch()"
    />
    <CrudFormModal
      :open="addAuthenticationOpen"
      :item="selectedTargetPort"
      :config="addAuthenticationConfig"
      title="Add Authentication"
      submit-label="Save"
      @open="(open) => (addAuthenticationOpen = open)"
      @submit="() => page.fetch()"
    />
  </div>
</template>

<script setup lang="ts">
import * as z from "zod";
import type { TargetPort, Authentication } from "~/types/models";
import type { CrudConfig, CrudTableColumn } from "~/types/crud";
import { useUserStore } from "~/store/user";

const userStore = useUserStore();
const backend = useBackend();
const route = useRoute();
const validation = useValidation();
const authenticationApi = useApi("/api/authentications/");
const page = ref();
const deleteAuthenticationOpen = ref(false);
const addAuthenticationOpen = ref(false);
const addAuthenticationConfig = ref({
  editForm: resolveComponent("FormAuthentication"),
  entityName: "Authentication",
  endpoint: "/api/authentications/",
});
const selectedTargetPort = ref();

const config: CrudConfig<TargetPort> = reactive({
  endpoint: "/api/target-ports/",
  entityName: "Target Port",
  entityNamePlural: "Target Ports",
  icon: "i-lucide-ethernet-port",
  tableColumns: [
    {
      accessorKey: "id",
      header: "ID",
      icon: "i-lucide-hash",
      cell: ({ row }) =>
        h("span", { class: "font-medium" }, row.getValue("id")),
    },
    {
      accessorKey: "port",
      header: "Port",
      icon: "i-lucide-ethernet-port",
      cell: ({ row }) => {
        const port = row.getValue("port") as number;
        return h("div", { class: "flex items-center gap-2" }, [
          h(resolveComponent("UIcon"), {
            name: backend.getPortIcon(port),
            class: "w-4 h-4",
          }),
          h("span", { class: "font-medium" }, port.toString()),
        ]);
      },
    },
    {
      accessorKey: "path",
      header: "Path",
      icon: "i-lucide-slash",
      cell: ({ row }) => {
        const path = row.getValue("path") as string;
        return h("span", { class: "font-medium" }, path);
      },
    },
    {
      accessorKey: "authentication.type",
      header: "Authentication",
      icon: "i-lucide-key",
      cell: ({ row }) => {
        const targetPort = row.original as TargetPort;
        const auth = targetPort.authentication;
        return h("span", { class: "font-medium" }, auth ? auth.type : "None");
      },
    },
  ] as CrudTableColumn<TargetPort>[],
  tableColumnsVisibility: { id: false },
  searchable: true,
  searchPlaceholder: "Search target ports...",
  filters: [],
  defaultFilters: { target: route.params.target_id },
  ordering: ["id", "port", "path"],
  defaultOrdering: "-id",
  defaultBody: { target: route.params.target_id },
  formFields: [
    {
      key: "port",
      label: "Port",
      type: "number",
      required: true,
      placeholder: 80,
    },
    {
      key: "path",
      label: "Path",
      type: "text",
      required: false,
      placeholder: "/",
    },
  ],
  formSchema: z.object({
    port: z.number().min(0).max(65535).optional(),
    path: validation.path("path", false, 100),
  }),
  createForm: resolveComponent("FormTargetPort"),
  canRead: true,
  canEdit: false,
  canCreate: userStore.is_auditor,
  canDelete: userStore.is_auditor,
  deleteMessage: (targetPort: TargetPort) => [
    {
      component: h(
        "p",
        { class: "text-gray-900 dark:text-white font-medium" },
        "Are you sure you want to delete this target port?",
      ),
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "neutral",
        variant: "subtle",
        description: `Port ${targetPort.port}`,
        ui: { root: "text-center font-bold" },
        class: "mt-4",
      },
    },
    {
      component: resolveComponent("UAlert"),
      props: {
        color: "error",
        icon: "i-lucide-triangle-alert",
        title: "Permanent deletion",
        description:
          "All associated data including assets, findings, and scans will be permanently deleted. This action cannot be undone.",
        class: "mt-4",
      },
    },
  ],
  customDropdownActions: (TargetPort: TargetPort) => {
    if (!userStore.is_auditor) return [];
    return [
      TargetPort.authentication
        ? {
            label: "Remove authentication",
            icon: "i-lucide-lock-keyhole-open",
            color: "error",
            onSelect: (item: TargetPort) => {
              selectedTargetPort.value = item;
              deleteAuthenticationOpen.value = true;
            },
          }
        : {
            label: "Add authentication",
            icon: "i-lucide-key",
            color: "success",
            onSelect: (item: TargetPort) => {
              selectedTargetPort.value = item;
              addAuthenticationOpen.value = true;
            },
          },
    ];
  },
});
</script>
