<template>
  <div>
    <CrudPage disable-url-sync :config="integrationsConfig">
      <template #item="{ item }">
        <UPageCard
          :title="item.name"
          :description="item.description"
          variant="subtle"
          spotlight
          @click="
            () => {
              if (item.id in integrationsSettings) {
                openModal = true;
                selectedIntegration = item;
              }
            }
          "
        >
          <template #leading>
            <UAvatar :src="item.icon" :alt="item.name" />
          </template>
          <div class="absolute top-4 right-4">
            <div class="flex items-center gap-3">
              <USwitch
                :model-value="getIntegrationState(item)"
                :aria-label="`${getIntegrationState(item) ? 'Disable' : 'Enable'} ${item.name} integration`"
                @update:model-value="toggleIntegration(item, $event)"
                @click.stop
              />
              <UButton
                v-if="item.reference"
                icon="i-lucide-external-link"
                variant="ghost"
                color="neutral"
                size="xl"
                :aria-label="`Open ${item.name} documentation`"
                :to="item.reference"
                target="_blank"
                external
              />
            </div>
          </div>
        </UPageCard>
      </template>
    </CrudPage>
    <LazyCrudFormModal
      v-if="currentIntegrationSettings"
      :open="openModal"
      :item="currentIntegrationSettings.item"
      :config="currentIntegrationSettings.config"
      :api="currentIntegrationSettings.api"
      :title="selectedIntegration.name"
      @open="(open) => (openModal = open)"
      @submit="(data) => updateSettings(selectedIntegration.id, data)"
    >
      <template #before-close="{ loading }">
        <AvailabilityButton
          :ok="currentIntegrationSettings?.item?.is_available"
          :loading="loading"
        />
      </template>
    </LazyCrudFormModal>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import type {
  DefectDojoSettings,
  Integration,
  VirusTotalSettings,
} from "~/types/models";
import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";
import * as z from "zod";

const toast = useToast();
const userStore = useUserStore();
const integrations = useIntegrationsStore();
const validation = useValidation();
const api = useApi("/api/integrations/");
const openModal = ref(false);
const selectedIntegration = ref();
const cveCrowdDaysSpan = [1, 7, 30];
const integrationsSettings = ref({
  1: {
    config: {
      entityName: "DefectDojo",
      editFormFields: [
        {
          key: "server",
          label: "Server",
          type: "text",
          placeholder: "https://defectdojo.example.com",
          required: false,
          inputMode: "url",
        },
        {
          key: "api_token",
          label: "API Token",
          type: "password",
          placeholder: "Enter your DefectDojo API token",
          required: false,
        },
        {
          key: "tls_validation",
          label: "TLS Validation",
          type: "checkbox",
          required: false,
        },
        {
          key: "tag",
          label: "Tag",
          type: "text",
          placeholder: "Enter a tag",
          required: false,
        },
      ],
      editFormSchema: z.object({
        server: validation.target("server", false, 100).or(z.literal("")),
        api_token: validation.secret("api_token", false, 40).or(z.literal("")),
        tls_validation: z.boolean().optional(),
        tag: validation.name("tag", false, 200).or(z.literal("")),
      }),
    },
    api: useApi("/api/defectdojo/settings/"),
  },
  2: {
    config: {
      entityName: "NVD NIST",
      editFormFields: [
        {
          key: "api_token",
          label: "API Key",
          type: "password",
          placeholder: "Enter your NVD NIST API key",
          required: false,
          hint: "NVD NIST API rate limit is extended when used with an API key",
        },
      ],
      editFormSchema: z.object({
        api_token: validation.secret("api_token", false, 50).or(z.literal("")),
      }),
    },
  },
  4: {
    config: {
      entityName: "CVE Crowd",
      editFormFields: [
        {
          key: "api_token",
          label: "API Token",
          type: "password",
          placeholder: "Enter your CVE Crowd API token",
          required: false,
        },
        {
          key: "trending_span_days",
          label: "Trending Span",
          type: "select",
          required: true,
          options: cveCrowdDaysSpan.map((v) => ({
            value: v,
            label: `${v} day${v > 0 ? "s" : ""}`,
          })),
        },
        {
          key: "execute_per_execution",
          label: "Monitor each execution",
          type: "checkbox",
          required: true,
        },
      ],
      editFormSchema: z.object({
        api_token: validation.secret("api_token", false, 50).or(z.literal("")),
        trending_span_days: z.union(cveCrowdDaysSpan.map((v) => z.literal(v))),
        execute_per_execution: z.boolean(),
      }),
    },
  },
  5: {
    config: {
      entityName: "Virus Total",
      editFormFields: [
        {
          key: "api_token",
          label: "API Key",
          type: "password",
          placeholder: "Enter your Virus Total API key",
          required: false,
        },
      ],
      editFormSchema: z.object({
        api_token: validation.secret("api_token", false, 64).or(z.literal("")),
      }),
    },
  },
});
const currentIntegrationSettings = computed(() => {
  return selectedIntegration.value &&
    integrationsSettings.value[selectedIntegration.value.id]
    ? integrationsSettings.value[selectedIntegration.value.id]
    : null;
});
let enableIfAvailable;

onMounted(() => {
  fetch();
});

function fetch() {
  for (const [key, value] of Object.entries(integrationsSettings.value)) {
    const integrationApi = value.api
      ? value.api
      : useApi(
          `/api/${value.config.entityName.toLowerCase().replace(" ", "")}/`,
        );
    integrationsSettings.value[key]["api"] = integrationApi;
    integrationsSettings.value[key]["config"]["modalAvatar"] = () => ({
      src: selectedIntegration.value.icon,
      alt: selectedIntegration.value.name,
    });
    integrationApi.get("1/").then((response) => {
      integrationsSettings.value[key]["item"] = response;
    });
  }
}

function updateSettings(integrationId: number, data: Record<string, unknown>) {
  integrationsSettings.value[integrationId].item = data;
  if (integrationId === 1)
    integrations.updateDefectDojoSettings(data as DefectDojoSettings);
  else if (integrationId === 5)
    integrations.updateVirusTotalSettings(data as VirusTotalSettings);
  if (
    enableIfAvailable !== undefined &&
    enableIfAvailable.id === integrationId &&
    data.is_available
  ) {
    toggleIntegration(enableIfAvailable, true);
    enableIfAvailable = undefined;
  }
}

function getIntegrationState(item: Integration) {
  if (item.id in integrationsSettings.value) {
    const settings = integrationsSettings.value[item.id];
    return item.enabled && settings.item?.is_available;
  }
  return item.enabled;
}

function toggleIntegration(integration: Integration, enabled: boolean) {
  if (
    integration.id in integrationsSettings.value &&
    !integrationsSettings.value[integration.id].item.is_available
  ) {
    integration.enabled = false;
    openModal.value = true;
    selectedIntegration.value = integration;
    enableIfAvailable = integration;
  } else {
    api.update(`${integration.id}/`, { enabled: enabled }, {}).then(() => {
      integration.enabled = enabled;
      integrations.updateIntegration(integration.id, { enabled: enabled });
      toast.add({
        title: integration.name,
        description: `${integration.name} integration has been ${enabled ? "enabled" : "disabled"}`,
        color: enabled ? "success" : "warning",
      });
    });
  }
}

const integrationsConfig: CrudConfig<Integration> = reactive({
  endpoint: "/api/integrations/",
  entityName: "Integration",
  entityNamePlural: "Integrations",
  icon: "i-lucide-plug",
  useGrid: true,
  searchable: false,
  filters: [],
  ordering: [],
  canRead: userStore.is_admin,
  canCreate: false,
  canEdit: false,
  canDelete: false,
});
</script>
