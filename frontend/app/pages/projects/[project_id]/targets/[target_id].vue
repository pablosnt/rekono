<template>
  <div>
    <CrudHeader
      :api="api"
      :config="{
        entityNamePlural: target?.target,
        headerIcon: target
          ? backend.targetTypes.find((t) => t.value === target.type)?.icon
          : undefined,
      }"
      title-size-class="text-3xl"
    />
    <!-- TODO: Run tasks (per target, and per target port), links to tasks, notes and reports, add dropdown with generate report and take note -->
    <div class="space-y-14">
      <TargetPorts />
      <HttpHeaders
        :target="parseInt($route.params.target_id)"
        :can-read="true"
        :can-edit="userStore.is_auditor"
        :can-delete="userStore.is_auditor"
        :can-create="userStore.is_auditor"
        :show-access-denied-error="false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const userStore = useUserStore();
const route = useRoute();
const backend = useBackend();
const api = useApi("/api/");
const target = ref();

onMounted(() => {
  api.get(`targets/${route.params.target_id}/`).then((response) => {
    target.value = response;
  });
});
</script>
