<template>
  <CrudPage :config="config">
    <template #item="{ item }">
      <UPageCard
        :title="item.name"
        :description="`./${item.command}${item.script ? ` ${item.script}` : ''}`"
        variant="subtle"
        spotlight
        class="cursor-pointer"
        @click="onCardClick($event.target, item.reference)"
      >
        <template #leading>
          <UAvatar v-if="item.icon" :src="item.icon" />
          <UIcon
            v-else
            name="i-lucide-square-terminal"
            class="text-xl text-primary"
          />
        </template>
        <UBadge
          v-if="item.is_installed"
          icon="i-lucide-check"
          :label="item.version || 'Installed'"
          color="neutral"
          class="absolute top-4 right-4"
        />
        <div class="flex items-center justify-between mt-4">
          <TasksRunButton :tool="item" />
          <CrudLikes
            size="lg"
            :item-id="item.id"
            endpoint="/api/tools/"
            :liked="item.liked"
            :count="item.likes"
            @update="
              (liked: boolean, count: number) => {
                item.liked = liked;
                item.likes = count;
              }
            "
          />
        </div>
      </UPageCard>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import { useUserStore } from "~/store/user";
import type { Tool } from "~/types/models";

const userStore = useUserStore();
const utils = useUtils();

function onCardClick(target: HTMLElement, reference: string) {
  if (target.closest("button") || target.closest('[role="button"]')) {
    return;
  }
  window.open(reference, "_blank");
}

const config: CrudConfig<Tool> = reactive({
  endpoint: "/api/tools/",
  entityName: "Tool",
  entityNamePlural: "Tools",
  icon: "i-lucide-square-terminal",
  useGrid: true,
  searchable: true,
  searchPlaceholder: "Search tools...",
  filters: [
    {
      key: "stage",
      label: "Stage",
      icon: "i-lucide-layers",
      type: "select" as const,
      options: utils.stageOptions,
    },
    {
      key: "intensity",
      label: "Intensity",
      icon: "i-lucide-database-zap",
      type: "select" as const,
      options: utils.intensityOptions,
    },
    {
      key: "is_installed",
      label: "Installed",
      type: "checkbox" as const,
    },
    {
      key: "like",
      label: "Favourites",
      icon: "i-lucide-heart",
      type: "checkbox" as const,
    },
  ],
  ordering: ["id", "name", "command"],
  defaultOrdering: "-id",
  pageSize: 24,
  pageSizeOptions: [24, 48, 96],
  canRead: userStore.is_auditor,
  canCreate: false,
  canEdit: false,
  canDelete: false,
});
</script>
