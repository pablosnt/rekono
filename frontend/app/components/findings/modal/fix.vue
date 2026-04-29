<template>
  <UModal
    :open="open"
    :title="firstUpper(verb)"
    :ui="{ content: 'sm:max-w-3xl sm:max-h-xl', footer: 'justify-end' }"
    :loading="loading"
    @update:open="(value) => $emit('open', value)"
  >
    <template #body>
      <p class="text-gray-900 dark:text-white font-medium">
        {{
          `Are you sure you want to ${verb.toLowerCase()} this ${smartLowerCase(entityName)} ${isAsset ? "asset" : "finding"}?`
        }}
      </p>
      <UAlert
        color="info"
        icon="i-lucide-info"
        variant="subtle"
        :description="
          finding.is_fixed
            ? 'Related findings that were automatically fixed will also be reopened'
            : 'Related findings will be automatically marked as fixed too'
        "
        class="mt-4"
      />
    </template>
    <template #footer="{ close }">
      <UButton
        label="Cancel"
        color="neutral"
        variant="outline"
        @click="close"
      />
      <UButton
        :icon="
          fixVerb === 'Fix'
            ? finding.is_fixed
              ? 'i-lucide-rotate-ccw'
              : 'i-lucide-check-circle'
            : finding.is_fixed
              ? 'i-lucide-eye'
              : 'i-lucide-eye-off'
        "
        :color="
          fixVerb === 'Fix'
            ? finding.is_fixed
              ? 'primary'
              : 'success'
            : finding.is_fixed
              ? 'success'
              : 'primary'
        "
        :label="verb"
        :loading="loading"
        @click="switchFix"
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { Finding } from "~/types/models";

const props = defineProps<{
  api: typeof useApi;
  fixVerb: string;
  unfixVerb: string;
  finding: Finding;
  isAsset: boolean;
  entityName: string;
  open: boolean;
}>();
const emit = defineEmits<{
  open: [open: boolean];
  switched: [];
}>();

const toast = useToast();
const { refreshPanelCounts } = usePanel();
const loading = ref(false);
const verb = computed(() =>
  props.finding.is_fixed ? props.unfixVerb : props.fixVerb,
);

function switchFix() {
  loading.value = true;
  const method = props.finding.is_fixed ? props.api.remove : props.api.create;
  method(`${props.finding.id}/fix/`, {})
    .then(() => {
      emit("switched");
      emit("open", false);
      toast.add({
        title: `${firstUpper(smartLowerCase(props.entityName))} ${props.isAsset ? "asset" : "finding"} ${verb.value.toLowerCase()}ed`,
        color: props.finding.is_fixed ? "warning" : "success",
      });
      refreshPanelCounts();
    })
    .finally(() => {
      loading.value = false;
    });
}
</script>
