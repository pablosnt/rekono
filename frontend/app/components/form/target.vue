<template>
  <div class="space-y-4">
    <UFormField label="Targets" name="targetInput">
      <UTextarea
        v-model="targetInput"
        placeholder="Enter IP addresses, domains, networks, or IP ranges. Separate multiple targets with spaces, commas, or line breaks"
        rows="4"
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
  "validation-change": [isValid: boolean];
  "new-loading": [newLoading: boolean];
}>();

const genericApi = useApi("/api/");
const toast = useToast();
const validation = useValidation();
const schema = z.object({
  target: validation.target(),
});
const targetInput = ref("");
const targets = ref<string[]>([]);
const loading = ref(false);
const created = ref(0);

function addTargetsFromInput() {
  if (!targetInput.value.trim()) return;
  for (const target of targetInput.value
    .split(/[,\s\n]+/)
    .map((t) => t.trim())
    .filter((t) => t.length > 0)) {
    if (targets.value.includes(target)) continue;
    try {
      schema.parse({ target: target });
      targets.value.push(target);
    } catch {
      toast.add({
        title: "Invalid target",
        description: `Target '${target}' is not valid and has been discarded `,
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
  if (targets.value.length > 0) {
    loading.value = true;
    emit("new-loading", loading.value);
    created.value = 0;
    let errors = 0;
    for (const target of targets.value) {
      props.api
        .create("", { project: props.entity.id, target: target })
        .catch(() => {
          errors++;
        })
        .finally(() => {
          created.value++;
          if (created.value === targets.value.length) {
            if (errors > 0) {
              if (created.value > errors) {
                toast.add({
                  title: "Targets creation",
                  description: `${created.value - errors} targets were created successfully and ${errors} failed`,
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
                description: `${targets.value.length} targets were created successfully`,
                color: "success",
              });
            }
            loading.value = false;
            emit("new-loading", loading.value);
            genericApi.get(`projects/${props.entity.id}/`).then((project) => {
              emit("submit", project);
            });
          }
        });
    }
  }
}

defineExpose({ submit });
</script>
