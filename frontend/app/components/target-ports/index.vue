<template>
  <div>
    <CrudPage ref="page" disable-url-sync :config="config">
      <template v-if="userStore.is_auditor" #actions="{ item }">
        <TasksButton
          :project="{ id: parseInt(route.params.project_id) }"
          :target="{ id: parseInt(route.params.target_id) }"
          :target-port="item"
        />
      </template>
    </CrudPage>
    <LazyCrudDeleteModal
      :open="deleteAuthenticationOpen"
      :item="selectedTargetPort?.authentication"
      :config="{
        entityName: 'Authentication',
        deleteMessage: (authentication: Authentication) =>
          buildDeleteMessage('authentication', authentication.name),
      }"
      :api="authenticationApi"
      @open="(open) => (deleteAuthenticationOpen = open)"
      @deleted="page.fetch()"
    />
    <LazyCrudFormModal
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
const route = useRoute();
const validation = useValidation();
const authenticationApi = useApi("/api/authentications/");
const table = useTable();
const page = ref();
const deleteAuthenticationOpen = ref(false);
const addAuthenticationOpen = ref(false);
const addAuthenticationConfig = ref({
  editForm: resolveComponent("AuthenticationsForm"),
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
      cell: ({ row }) => table.valueCell(row.getValue("id")),
    },
    {
      accessorKey: "port",
      header: "Port",
      icon: "i-lucide-ethernet-port",
      cell: ({ row }) => {
        const port = row.getValue("port") as number;
        return table.iconAndValueCell(getPortIcon(port), port.toString());
      },
    },
    {
      accessorKey: "path",
      header: "Path",
      icon: "i-lucide-slash",
      cell: ({ row }) => table.valueCell(row.getValue("path")),
    },
    {
      accessorKey: "authentication",
      header: "Authentication",
      icon: "i-lucide-key",
      cell: ({ row }) =>
        table.valueCell(
          row.original.authentication
            ? row.original.authentication.type
            : "None",
        ),
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
  createForm: resolveComponent("TargetPortsForm"),
  canRead: true,
  canEdit: false,
  canCreate: userStore.is_auditor,
  canDelete: userStore.is_auditor,
  deleteMessage: (targetPort: TargetPort) =>
    buildDeleteMessage(
      "target port",
      `Port ${targetPort.port}`,
      "Permanent deletion",
      "All associated data including assets, findings, and scans will be permanently deleted. This action cannot be undone.",
    ),
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
