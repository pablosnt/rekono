<template>
  <UFormField name="Members" required>
    <USelectMenu
      v-model="newMembers"
      class="w-full"
      placeholder="Select new project members"
      :items="options"
      value-key="id"
      label-key="username"
      required
      multiple
      clear
      icon="i-lucide-users"
      size="xl"
      leading
      :disabled="options.length === 0"
      @update:model-value="$emit('validation-change', newMembers.length > 0)"
    >
      <template #item-label="{ item }">
        {{ getUserDisplayName(item) }}
      </template>
    </USelectMenu>
  </UFormField>
  <UProgress
    v-if="loading"
    v-model="created"
    :max="newMembers.length"
    status
    class="mt-5"
  />
</template>

<script setup lang="ts">
const props = defineProps<{
  api: typeof useApi;
  config: object;
  entity?: Record<string, unknown>;
}>();
const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
  "validation-change": [isValid: boolean];
  "new-loading": [newLoading: boolean];
}>();
const route = useRoute();
const addApi = useApi(`/api/projects/${route.params.project_id}/members/`);
const toast = useToast();
const newMembers = ref([]);
const options = ref([]);
const created = ref(0);
const loading = ref(false);

onMounted(() => {
  props.api
    .list("", { no_project: route.params.project_id, is_active: true }, true)
    .then((response) => {
      options.value = response.items;
    });
});

function submit() {
  if (newMembers.value.length > 0) {
    emit("new-loading", true);
    loading.value = true;
    created.value = 0;
    const total = newMembers.value.length;
    Promise.allSettled(
      newMembers.value.map((newMember) =>
        addApi.create(`${newMember}/`, {}).finally(() => created.value++),
      ),
    ).then((results) => {
      const errors = results.filter((r) => r.status === "rejected").length;
      if (errors > 0) {
        if (total > errors) {
          toast.add({
            title: "Members addition",
            description: `${total - errors} users were added to the project successfully and ${errors} failed`,
            color: "warning",
          });
        } else {
          toast.add({
            title: "Members addition",
            description: `${errors} users weren't added to the project`,
            color: "error",
          });
        }
      } else {
        toast.add({
          title: "Members addition",
          description: `${total} users were added to the project successfully`,
          color: "success",
        });
      }
      loading.value = false;
      emit("new-loading", false);
      emit("submit", {});
    });
  }
}

defineExpose({ submit });
</script>
