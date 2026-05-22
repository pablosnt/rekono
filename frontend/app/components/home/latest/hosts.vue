<template>
  <UPageCard variant="outline" :ui="{ container: 'min-w-0' }">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-base font-semibold text-highlighted">Latest Hosts</h2>
    </div>
    <UTable
      :data="hosts"
      :columns="columns"
      :ui="{ tbody: '[&>tr]:cursor-pointer' }"
      @select="
        (_, row) =>
          navigateTo(
            `/projects/${row.original.project}/hosts/${row.original.id}`,
          )
      "
    />
  </UPageCard>
</template>

<script setup lang="ts">
import { hostOS } from "~/constants";
import type { Host } from "~/types/models";

defineProps<{ hosts: Host[] }>();

const table = useTable();
const columns = [
  {
    accessorKey: "ip",
    header: table.iconAndValueHeader("IP", "i-lucide-server"),
    cell: ({ row }: { row: { original: Host } }) =>
      table.valueCell(row.original.ip),
  },
  {
    accessorKey: "domain",
    header: table.iconAndValueHeader("Domain", "i-lucide-globe"),
    cell: ({ row }: { row: { original: Host } }) =>
      table.valueCell(row.original.domain),
  },
  {
    accessorKey: "os",
    header: table.iconAndValueHeader("OS", "i-lucide-monitor"),
    cell: ({ row }: { row: { original: Host } }) => {
      const osConfig = hostOS.find((o) => o.value === row.original.os_type);
      return table.iconAndValueCell(
        osConfig?.icon,
        row.original.os,
        osConfig?.color,
      );
    },
  },
];
</script>
