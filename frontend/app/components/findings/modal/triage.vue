<template>
  <UModal
    v-if="finding"
    :open="open"
    title="Triage"
    :description="
      finding.triage_by && finding.triage_date
        ? `Triaged by ${finding.triage_by.username} ${useTimeAgo(new Date(finding.triage_date)).value}`
        : undefined
    "
    :ui="{ content: 'sm:max-w-3xl sm:max-h-xl', footer: 'justify-end' }"
    :loading="loading"
    @update:open="(value) => $emit('open', value)"
  >
    <template #body>
      <CrudForm
        ref="form"
        :api="api"
        :entity="finding"
        :config="config"
        @submit="
          () => {
            $emit('triaged');
            $emit('open', false);
          }
        "
        @new-loading="(newLoading) => (loading = newLoading)"
        @validation-change="(isValid) => (valid = isValid)"
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
        color="primary"
        label="Triage"
        :loading="loading"
        :disabled="!valid"
        @click="
          loading = true;
          form?.submit();
        "
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useTimeAgo } from "@vueuse/core";
import type { Finding } from "~/types/models";
import * as z from "zod";

const props = defineProps<{
  open: boolean;
  api: typeof useApi;
  finding: Finding;
  entityName: string;
}>();
defineEmits<{
  open: [open: boolean];
  triaged: [];
}>();

const backend = useBackend();
const validation = useValidation();
const loading = ref(false);
const valid = ref(false);
const form = ref();

const config = {
  entityName: props.entityName,
  editFormFields: [
    {
      key: "triage_status",
      label: "Triage status",
      type: "select",
      required: true,
      options: backend.triageStatuses,
      labelKey: "value",
    },
    {
      key: "triage_comment",
      label: "Comment",
      type: "textarea",
      placeholder: "Triage comments, notes or arguments",
      required: false,
    },
  ],
  editFormSchema: z.object({
    triage_status: z.enum(
      backend.triageStatuses.map((s) => s.value) as [string, ...string[]],
    ),
    triage_comment: validation.text("triage_comment", false, 300).optional(),
  }),
};
</script>
