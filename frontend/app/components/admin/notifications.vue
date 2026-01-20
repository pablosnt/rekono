<template>
  <CrudPage
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
      <UProgress v-if="loadingSmtp || loadingTelegram" />

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
            <div class="flex items-center justify-end">
              <div class="w-45">
                <UIcon name="i-lucide-mail" class="text-xl text-neutral" />
              </div>
              <div class="flex w-40 justify-end items-center gap-3">
                <UtilsOkOrKo :ok="smtpSettings.is_available" />
              </div>
            </div>
          </template>
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
            <div class="flex items-center justify-end">
              <div class="w-45">
                <UIcon
                  name="i-simple-icons-telegram"
                  class="text-xl text-info"
                />
              </div>
              <div class="flex w-40 justify-end items-center gap-3">
                <UtilsOkOrKo :ok="telegramSettings.is_available" />
                <UButton
                  v-if="telegramSettings.is_available"
                  icon="i-lucide-external-link"
                  variant="ghost"
                  color="gray"
                  size="lg"
                  :to="`https://t.me/${telegramSettings.bot}`"
                  target="_blank"
                  external
                />
              </div>
            </div>
          </template>
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
      <CrudFormModal
        v-if="selectedSettings"
        :open="openModal"
        :item="selectedSettings"
        :config="selectedConfig"
        :api="selectedApi"
        :title="selectedTitle"
        @open="(open) => (openModal = open)"
        @submit="
          (data) =>
            selectedTitle === 'SMTP'
              ? (smtpSettings = data)
              : (telegramSettings = data)
        "
      >
        <template #before-close="{ loading }">
          <UtilsOkOrKo
            :ok="selectedSettings?.is_available"
            :loading="loading"
          />
        </template>
      </CrudFormModal>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import * as z from "zod";
import { useUserStore } from "~/store/user";

const smtpApi = useApi("/api/smtp/");
const telegramApi = useApi("/api/telegram/settings/");
const validate = useValidation();
const userStore = useUserStore();
const loadingSmtp = ref(false);
const loadingTelegram = ref(false);
const openModal = ref(false);
const smtpSettings = ref();
const smtpConfig = ref({
  entityName: "SMTP",
  editFormFields: [
    {
      key: "host",
      label: "Host",
      type: "text",
      placeholder: "smtp.example.com",
      required: false,
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
    host: validate.target("host", false, 100).or(z.literal("")),
    port: z.number().min(0).max(65535).optional(),
    username: validate.name("username", false, 100).or(z.literal("")),
    password: validate.secret("password", false, 200).or(z.literal("")),
    tls: z.boolean().optional(),
  }),
  modalIcon: "i-lucide-mail",
  modalIconClass: "text-xl text-neutral",
});
const telegramSettings = ref();
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
    token: validate.secret("token", false, 200).or(z.literal("")),
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
