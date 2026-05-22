<template>
  <CrudPage
    disable-url-sync
    :config="{
      entityNamePlural: 'Notifications',
      entityName: 'Notification',
      canRead: userStore.is_admin,
      canEdit: false,
      canDelete: false,
      canCreate: false,
      showAccessDeniedError: false,
    }"
  >
    <template #content>
      <UProgress
        :class="[
          loadingSmtp || loadingTelegram ? 'visible' : 'invisible',
          'mb-1',
        ]"
      />
      <UPageGrid v-if="smtpSettings && telegramSettings">
        <UPageCard
          title="SMTP"
          :description="
            smtpSettings.is_available
              ? smtpSettings.host
              : 'Configure your SMTP server in order to send email messages'
          "
          variant="subtle"
          spotlight
          @click="
            () => {
              openModal = true;
              selectedApi = smtpApi;
              selectedSettings = smtpSettings;
              selectedConfig = smtpConfig;
              selectedTitle = 'SMTP';
            }
          "
        >
          <template #leading>
            <UIcon name="i-lucide-mail" class="text-xl text-neutral" />
          </template>
          <div class="absolute top-4 right-4">
            <AvailabilityButton :ok="smtpSettings.is_available" />
          </div>
        </UPageCard>
        <UPageCard
          title="Telegram"
          :description="
            telegramSettings.is_available
              ? `@${telegramSettings.bot}`
              : 'Configure your Telegram token in order to enable the Rekono bot and receive Telegram notifications'
          "
          variant="subtle"
          spotlight
          @click="
            () => {
              openModal = true;
              selectedApi = telegramApi;
              selectedSettings = telegramSettings;
              selectedConfig = telegramConfig;
              selectedTitle = 'Telegram';
            }
          "
        >
          <template #leading>
            <UIcon name="i-simple-icons-telegram" class="text-xl text-info" />
          </template>
          <div class="absolute top-4 right-4">
            <div class="flex items-center gap-3">
              <AvailabilityButton :ok="telegramSettings.is_available" />
              <UButton
                v-if="telegramSettings.is_available"
                icon="i-lucide-external-link"
                variant="ghost"
                color="neutral"
                size="xl"
                :to="`https://t.me/${telegramSettings.bot}`"
                target="_blank"
                external
                aria-label="Open Telegram bot"
              />
            </div>
          </div>
          <template #description>
            <ULink
              v-if="telegramSettings.is_available"
              :to="`https://t.me/${telegramSettings.bot}`"
              target="_blank"
              >@{{ telegramSettings.bot }}
            </ULink>
            <p v-else>
              Configure your Telegram token in order to enable the Rekono bot
              and receive Telegram notifications
            </p>
          </template>
        </UPageCard>
      </UPageGrid>
      <LazyCrudFormModal
        v-if="selectedSettings"
        :open="openModal"
        :item="selectedSettings"
        :config="selectedConfig"
        :api="selectedApi"
        :title="selectedTitle"
        @open="(open) => (openModal = open)"
        @submit="
          (data) => {
            if (selectedTitle === 'SMTP') {
              smtpSettings = data;
              integrations.updateSmtpSettings(data);
            } else {
              telegramSettings = data;
              integrations.updateTelegramSettings(data);
            }
          }
        "
      >
        <template #before-close="{ loading }">
          <AvailabilityButton
            :ok="selectedSettings?.is_available"
            :loading="loading"
          />
        </template>
      </LazyCrudFormModal>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import * as z from "zod";
import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";

const smtpApi = useApi("/api/smtp/");
const telegramApi = useApi("/api/telegram/settings/");
const validation = useValidation();
const userStore = useUserStore();
const integrations = useIntegrationsStore();
const loadingSmtp = ref(false);
const loadingTelegram = ref(false);
const openModal = ref(false);
const smtpSettings = ref(integrations.smtp);
const smtpConfig = ref({
  entityName: "SMTP",
  editFormFields: [
    {
      key: "host",
      label: "Host",
      type: "text",
      placeholder: "smtp.example.com",
      required: false,
      inputMode: "url",
    },
    {
      key: "port",
      label: "Port",
      type: "number",
      placeholder: "587",
      required: false,
      min: 0,
      max: 65535,
    },
    {
      key: "username",
      label: "Username",
      type: "text",
      placeholder: "Enter the SMTP server username",
      required: false,
    },
    {
      key: "password",
      label: "Password",
      type: "password",
      placeholder: "Enter the SMTP server password",
      required: false,
    },
    {
      key: "tls",
      label: "Use TLS",
      type: "checkbox",
      required: false,
    },
  ],
  editFormSchema: z.object({
    host: validation.target("host", false, 100).or(z.literal("")),
    port: z.number().min(0).max(65535).optional(),
    username: validation.name("username", false, 100).or(z.literal("")),
    password: validation.secret("password", false, 200).or(z.literal("")),
    tls: z.boolean().optional(),
  }),
  modalIcon: "i-lucide-mail",
  modalIconClass: "text-xl text-neutral",
});
const telegramSettings = ref(integrations.telegram);
const telegramConfig = ref({
  entityName: "Telegram",
  editFormFields: [
    {
      key: "token",
      label: "Bot token",
      type: "password",
      placeholder: "Enter your Telegram bot token",
      required: false,
      hint: "Create a Telegram bot and paste here the token shared by the @BotFather",
    },
  ],
  editFormSchema: z.object({
    token: validation.secret("token", false, 200).or(z.literal("")),
  }),
  modalIcon: "i-simple-icons-telegram",
  modalIconClass: "text-xl text-info",
});
const selectedApi = ref();
const selectedSettings = ref();
const selectedTitle = ref();
const selectedConfig = ref();

function fetch() {
  loadingSmtp.value = true;
  smtpApi
    .get("1/")
    .then((response) => (smtpSettings.value = response))
    .finally(() => (loadingSmtp.value = false));
  loadingTelegram.value = true;
  telegramApi
    .get("1/")
    .then((response) => (telegramSettings.value = response))
    .finally(() => (loadingTelegram.value = false));
}

onMounted(() => {
  fetch();
});
</script>
