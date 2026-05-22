<template>
  <UPageCard variant="outline" :ui="{ container: 'min-w-0' }">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-base font-semibold text-highlighted">
        Latest Vulnerabilities
      </h2>
    </div>
    <UTable
      :data="vulnerabilities"
      :columns="columns"
      :ui="{ tbody: '[&>tr]:cursor-pointer' }"
      @select="
        (_, row) =>
          navigateTo(
            `/projects/${row.original.project}/vulnerabilities/${row.original.id}`,
          )
      "
    />
  </UPageCard>
</template>

<script setup lang="ts">
import type { Vulnerability } from "~/types/models";
import { hostOS, severities } from "~/constants";

defineProps<{ vulnerabilities: Vulnerability[] }>();

const table = useTable();
const columns = [
  {
    id: "host",
    header: table.iconAndValueHeader("Host", "i-lucide-server"),
    cell: ({ row }: { row: { original: Vulnerability } }) => {
      const host =
        row.original.port?.host || row.original.technology?.port?.host;
      const config = hostOS.find((c) => c.value === host.os_type);
      return table.iconAndValueCell(
        config?.icon || "i-lucide-server",
        host.domain || host.ip,
        config?.color || "neutral",
      );
    },
  },
  {
    accessorKey: "name",
    header: table.iconAndValueHeader("Name", "i-lucide-case-sensitive"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) =>
      table.valueCell(row.getValue("name") as string),
  },
  {
    accessorKey: "severity",
    header: table.iconAndValueHeader("Severity", "i-lucide-shield-alert"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) => {
      const value = row.getValue("severity") as string | undefined;
      const severity = severities.find((s) => s.value === value);
      return table.badgeCell(value, severity?.icon, severity?.color);
    },
  },
  {
    accessorKey: "cve",
    header: table.iconAndValueHeader("CVE", "i-lucide-hash"),
    cell: ({ row }: { row: { getValue: (key: string) => unknown } }) =>
      table.valueCell(row.getValue("cve") as string | undefined),
  },
];
</script>
