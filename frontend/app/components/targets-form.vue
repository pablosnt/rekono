<template>
  <div class="space-y-4">
    <UFormField label="Targets" name="targetInput">
      <UTextarea
        v-model="targetInput"
        placeholder="Enter IP addresses, domains, networks, or IP ranges. Separate multiple targets with spaces, commas, or line breaks"
        rows="4"
        inputmode="url"
        class="w-full"
      />
    </UFormField>
    <div class="flex justify-end">
      <UButton
        icon="i-lucide-plus"
        color="primary"
        variant="outline"
        label="Add Targets"
        :disabled="!targetInput.trim()"
        @click="addTargetsFromInput"
      />
    </div>
    <div v-if="targets.length > 0" class="space-y-4">
      <ULabel>Added Targets ({{ targets.length }})</ULabel>
      <div class="flex flex-wrap gap-2 mt-3">
        <UBadge
          v-for="(target, index) in targets"
          :key="index"
          variant="subtle"
          color="primary"
          >{{ target }}
          <template #trailing>
            <UButton
              icon="i-lucide-x"
              variant="ghost"
              color="neutral"
              size="sm"
              :aria-label="`Discard target ${target}`"
              @click="removeTarget(index)"
            />
          </template>
        </UBadge>
      </div>
    </div>
    <UProgress v-if="loading" v-model="created" :max="targets.length" status />
    <UEmpty
      v-if="targets.length === 0"
      title="No targets added yet"
      description="Add targets using the input field above"
      icon="i-lucide-locate-fixed"
      size="sm"
      class="mt-5"
    />
  </div>
</template>

<script setup lang="ts">
import * as z from "zod";

const props = defineProps<{
  api: typeof useApi;
  config: object;
  entity?: Record<string, unknown>;
}>();
const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
  "new-submit-label": [newSubmitLabel: string];
  "validation-change": [isValid: boolean];
  "new-loading": [newLoading: boolean];
}>();

const genericApi = useApi("/api/");
const toast = useToast();
const validation = useValidation();
const route = useRoute();
const schema = z.object({
  target: validation.target(),
});
const targetInput = ref("");
const targets = ref<string[]>([]);
const loading = ref(false);
const created = ref(0);
const project = ref(
  props.entity
    ? props.entity
    : route.params.project_id
      ? { id: route.params.project_id }
      : null,
);

function addTargetsFromInput() {
  if (!targetInput.value.trim()) return;
  emit("new-submit-label", "Create");
  for (const target of targetInput.value
    .split(/[,\s\n]+/u)
    .map((t) => t.trim())
    .filter((t) => t.length > 0)) {
    if (targets.value.includes(target)) continue;
    try {
      schema.parse({ target: target });
      targets.value.push(target);
    } catch {
      toast.add({
        title: "Invalid target",
        description: `Target '${target}' is not valid and has been discarded`,
        color: "error",
      });
    }
  }
  targetInput.value = "";
  emit("validation-change", targets.value.length > 0);
}

function removeTarget(index: number) {
  targets.value.splice(index, 1);
  if (targets.value.length === 0) {
    emit("validation-change", false);
  }
}

function submit() {
  if (targetInput.value.trim()) {
    addTargetsFromInput();
  }
  if (project.value) {
    if (targets.value.length > 0) {
      loading.value = true;
      emit("new-loading", loading.value);
      created.value = 0;
      const total = targets.value.length;
      Promise.allSettled(
        targets.value.map((target) =>
          props.api
            .create("", { project: project.value.id, target: target })
            .finally(() => created.value++),
        ),
      ).then((results) => {
        const createdTargets = results
          .filter((r) => r.status === "fulfilled")
          .map((r) => r.value);
        const errors = results.filter((r) => r.status === "rejected").length;
        if (errors > 0) {
          if (total > errors) {
            toast.add({
              title: "Targets creation",
              description: `${total - errors} targets were created successfully and ${errors} failed`,
              color: "warning",
            });
          } else {
            toast.add({
              title: "Targets creation failed",
              description: `${errors} targets weren't created`,
              color: "error",
            });
          }
        } else {
          toast.add({
            title: "Targets created successfully",
            description: `${total} targets were created successfully`,
            color: "success",
          });
        }
        loading.value = false;
        emit("new-loading", loading.value);
        genericApi.get(`projects/${project.value.id}/`).then((response) => {
          emit("submit", {
            project: response,
            targets: createdTargets,
          });
        });
      });
    } else {
      emit("submit", { project: project.value, targets: [] });
    }
  }
}

defineExpose({ submit });
</script>
