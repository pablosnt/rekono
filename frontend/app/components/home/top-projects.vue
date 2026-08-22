<template>
  <UPageCard variant="outline" :ui="{ container: 'min-w-0' }">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-base font-semibold text-highlighted">Top Projects</h2>
      <div class="flex items-center gap-2">
        <template v-if="userStore.is_admin">
          <UButton
            icon="i-lucide-plus"
            aria-label="Create project"
            @click="$emit('create')"
          />
        </template>
        <UButton
          icon="i-lucide-external-link"
          color="neutral"
          variant="outline"
          aria-label="View all projects"
          to="/projects"
        />
      </div>
    </div>
    <UTable
      :data="projects"
      :columns="projectColumns"
      :ui="{ tbody: '[&>tr]:cursor-pointer' }"
      @select="(_, row) => navigateTo(`/projects/${row.original.id}`)"
    />
  </UPageCard>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";
import type { Project } from "~/types/models";

defineEmits<{ create: [] }>();

const userStore = useUserStore();
const table = useTable();

const projects = useState<Project[]>("top-projects", () => []);
const projectColumns = [
  {
    accessorKey: "name",
    header: table.iconAndValueHeader("Name", "i-lucide-case-sensitive"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) =>
      table.valueCell(row.getValue("name") as string),
  },
  {
    accessorKey: "tags",
    header: table.iconAndValueHeader("Tags", "i-lucide-tag"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) =>
      h(resolveComponent("Tags"), { tags: row.getValue("tags") }),
  },
  {
    accessorKey: "targets",
    header: table.iconAndValueHeader("Targets", "i-lucide-locate-fixed"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) =>
      table.valueCell((row.getValue("targets") as number[]).length),
  },
];
</script>
