<template>
  <div>
    <CrudPage :config="integrationsConfig">
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
            <div class="flex items-center justify-end">
              <div class="w-45">
                <UAvatar :src="item.icon" />
              </div>
              <div class="flex w-40 justify-end items-center gap-3">
                <USwitch
                  :model-value="getIntegrationState(item)"
                  @update:model-value="toggleIntegration(item, $event)"
                  @click.stop
                />
                <UButton
                  v-if="item.reference"
                  icon="i-lucide-external-link"
                  variant="ghost"
                  color="gray"
                  size="lg"
                  :to="item.reference"
                  target="_blank"
                  external
                />
              </div>
            </div>
          </template>
        </UPageCard>
      </template>
    </CrudPage>
    <CrudFormModal
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
        <UTooltip
          :text="
            currentIntegrationSettings?.item?.is_available
              ? 'Available'
              : 'Not available. Change connection settings'
          "
        >
          <UButton
            :color="
              currentIntegrationSettings?.item?.is_available
                ? 'success'
                : 'error'
            "
            variant="ghost"
            :loading="loading"
            :icon="
              currentIntegrationSettings?.item?.is_available
                ? 'i-lucide-check'
                : 'i-lucide-unplug'
            "
          />
        </UTooltip>
      </template>
    </CrudFormModal>
  </div>
</template>

<script setup lang="ts">
import type { CrudConfig } from "~/types/crud";
import type { Integration } from "~/types/integrations";
import { useUserStore } from "~/store/user";
import * as z from "zod";

const userStore = useUserStore();
const validation = useValidation();
const api = useApi("/api/integrations/");
const openModal = ref(false);
const selectedIntegration = ref();
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
        {
          key: "test_type",
          label: "Test Type",
          type: "text",
          placeholder: "Enter test type",
          required: false,
        },
        {
          key: "test",
          label: "Test",
          type: "text",
          placeholder: "Enter test name",
          required: false,
        },
      ],
      editFormSchema: z.object({
        server: validation.target("server", false, 100).or(z.literal("")),
        api_token: validation.secret("api_token", false, 40).or(z.literal("")),
        tls_validation: z.boolean().optional(),
        tag: validation.name("tag", false, 200).or(z.literal("")),
        test_type: validation.name("test_type", false, 200).or(z.literal("")),
        test: validation.name("test", false, 200).or(z.literal("")),
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
          label: "Trending Span Days",
          type: "number",
          placeholder: "Enter number of days (1-7)",
          required: true,
          min: 1,
          max: 7,
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
        trending_span_days: z
          .number()
          .min(1, "Must be at least 1")
          .max(7, "Must be at most 7"),
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
let enableIfAvailable = undefined;

onMounted(() => {
  fetch();
});

function fetch() {
  for (const [key, value] of Object.entries(integrationsSettings.value)) {
    const api = !value.api
      ? useApi(
          `/api/${value.config.entityName.toLowerCase().replace(" ", "")}/`,
        )
      : value.api;
    integrationsSettings.value[key]["api"] = api;
    integrationsSettings.value[key]["config"]["modalAvatar"] = () => ({
      src: selectedIntegration.value.icon,
    });
    api.get("1/").then((response) => {
      integrationsSettings.value[key]["item"] = response;
    });
  }
}

function updateSettings(integrationId: number, data: Record<string, unknown>) {
  integrationsSettings.value[integrationId].item = data;
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
    api
      .update(`${integration.id}/`, { enabled: enabled }, {}, "Integration")
      .then(() => {
        integration.enabled = enabled;
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
