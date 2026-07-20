<template>
  <UModal
    v-if="
      integrations.defectdojo.integration?.enabled &&
      integrations.defectdojo.settings?.is_available
    "
    :ui="{ content: 'sm:max-w-3xl sm:max-h-xl', footer: 'justify-end' }"
  >
    <UTooltip
      text="Configure DefectDojo sync"
      :content="{ side: 'left', sideOffset: 8, collisionPadding: 8 }"
    >
      <UButton variant="ghost" aria-label="Configure DefectDojo sync">
        <UChip
          inset
          size="xl"
          position="bottom-right"
          :color="sync ? 'success' : 'error'"
        >
          <UAvatar :src="integrations.defectdojo.integration.icon" size="lg" />
        </UChip>
      </UButton>
    </UTooltip>
    <template #header="{ close }">
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-2">
          <UAvatar
            :src="integrations.defectdojo.integration.icon"
            size="xl"
            :alt="integrations.defectdojo.integration.name"
          />
          <h2 class="text-gray-900 dark:text-white font-bold text-lg">
            DefectDojo Synchronization
          </h2>
        </div>
        <div class="flex items-center gap-2">
          <DefectdojoLink
            v-if="sync"
            :id="sync.product_id"
            entity="product"
            icon="i-lucide-external-link"
          />
          <UButton
            icon="i-lucide-x"
            variant="ghost"
            color="neutral"
            aria-label="Close"
            @click="close"
          />
        </div>
      </div>
    </template>
    <template #body="{ close }">
      <UAlert
        color="info"
        variant="subtle"
        icon="i-lucide-info"
        description="If engagement is not configured, Rekono will create one automatically per target"
        class="mb-3"
      />
      <CrudForm
        ref="form"
        :api="api"
        :config="config"
        :entity="sync"
        @submit="
          $emit('update');
          close();
        "
        @validation-change="(isValid) => (valid = isValid)"
        @new-loading="(newLoading) => (loading = newLoading)"
      />
    </template>
    <template #footer="{ close }">
      <UButton
        v-if="sync"
        label="Disable"
        color="primary"
        variant="outline"
        @click="openDelete = true"
      />
      <UButton
        :label="sync ? 'Close' : 'Cancel'"
        color="neutral"
        :variant="sync ? undefined : 'outline'"
        @click="close"
      />
      <UButton
        v-if="!sync"
        color="info"
        label="Enable Sync"
        :disabled="!valid"
        :loading="loading"
        @click="
          loading = true;
          form?.submit();
        "
      />
      <LazyCrudDeleteModal
        :open="openDelete"
        :item="sync"
        :config="deleteConfig"
        :api="api"
        @open="(open) => (openDelete = open)"
        @deleted="
          $emit('update');
          close();
        "
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useIntegrationsStore } from "~/store/integrations";
import type { DefectDojoSync } from "~/types/models";
import * as z from "zod";

const props = defineProps<{ sync?: DefectDojoSync }>();
defineEmits<{ update: [] }>();

const integrations = useIntegrationsStore();
const api = useApi("/api/defectdojo/sync/");
const route = useRoute();
const form = ref();
const config = computed(() => ({
  entityName: "DefectDojo sync",
  formFields: [
    {
      key: "product_id",
      label: "Product ID",
      type: "number",
      required: true,
      placeholder: 1,
      min: 1,
      disabled: Boolean(props.sync),
    },
    {
      key: "engagement_id",
      label: "Engagement ID",
      type: "number",
      required: false,
      placeholder: 1,
      min: 1,
      hint: "If empty one will be automatically created per target",
      disabled: Boolean(props.sync),
    },
    {
      key: "reimport",
      label: "Use reimport instead of import operations",
      type: "checkbox",
      required: false,
      disabled: Boolean(props.sync),
    },
    {
      key: "close_old_findings",
      label: "Close old findings",
      type: "checkbox",
      required: false,
      disabled: Boolean(props.sync),
    },
  ],
  formSchema: z.object({
    product_id: z.number().min(1),
    engagement_id: z.number().min(1).optional(),
    reimport: z.boolean().optional(),
    close_old_findings: z.boolean().optional(),
  }),
  defaultBody: { project: route.params.project_id },
}));
const valid = ref(false);
const loading = ref(false);
const openDelete = ref(false);
const deleteConfig = {
  entityName: "DefectDojo Sync",
  deleteVerb: "Disable",
  deleteMessage: () =>
    buildDeleteMessage(
      "DefectDojo Sync",
      undefined,
      undefined,
      "New findings won't be imported in DefectDojo",
      "Disable",
    ),
};

onMounted(integrations.fetchDefectDojo);
</script>
