<template>
  <UPageCard variant="outline" :ui="{ container: 'min-w-0' }">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-base font-semibold text-highlighted">Latest Scans</h2>
      <TasksButton v-if="userStore.is_auditor" not-rounded />
    </div>
    <UTable
      :data="tasks"
      :columns="columns"
      :ui="{ tbody: '[&>tr]:cursor-pointer' }"
      @select="
        (_, row) =>
          navigateTo(
            `/projects/${row.original.target.project}/scans/${row.original.id}`,
          )
      "
    />
  </UPageCard>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import { executionStatuses, targetTypes } from "~/constants";
import type { Task } from "~/types/models";

defineProps<{ tasks: Task[] }>();

const userStore = useUserStore();
const table = useTable();
const columns = [
  {
    id: "scanner",
    header: table.iconAndValueHeader("Scanner", "i-lucide-terminal"),
    cell: ({ row }: { row: { original: Task } }) =>
      row.original.process
        ? table.valueCell(row.original.process.name)
        : table.toolCell(
            row.original.configuration?.tool,
            row.original.configuration,
          ),
  },
  {
    id: "target",
    header: table.iconAndValueHeader("Target", "i-lucide-locate-fixed"),
    cell: ({ row }: { row: { original: Task } }) => {
      let label = row.original.target?.target;
      if (row.original.target_port) {
        label += `:${row.original.target_port.port}`;
        if (row.original.target_port.path) {
          label +=
            row.original.target_port.path[0] === "/"
              ? row.original.target_port.path
              : `/${row.original.target_port.path}`;
        }
      }
      const icon =
        targetTypes.find((t) => t.value === row.original.target?.type)?.icon ||
        "i-lucide-locate-fixed";
      return table.iconAndValueCell(label, icon);
    },
  },
  {
    id: "status",
    header: table.iconAndValueHeader("Status", "i-lucide-activity"),
    cell: ({ row }: { row: { original: Task } }) => {
      const status = executionStatuses.find(
        (s) => s.value === row.original.status,
      );
      return row.original.status === "Running"
        ? h(resolveComponent("UProgress"), {
            status: true,
            modelValue: row.original.progress,
            max: 100,
            color: "warning",
          })
        : table.badgeCell(status?.value, status?.icon, status?.color);
    },
  },
];
</script>
